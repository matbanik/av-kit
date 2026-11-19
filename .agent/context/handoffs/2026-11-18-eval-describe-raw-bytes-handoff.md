---
date: "2026-11-18"
project: "2026-11-18-eval-describe-raw-bytes"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md"
build_plan_section: "none (eval tooling and run-book debt; no MEU, D-1196, grouping D-1199)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-17-e2e-pointer-flakes-handoff.md"
---

# Handoff: 2026-11-18-eval-describe-raw-bytes-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. Session 95 is eval tooling and run-book debt with no MEU (triage D-1196, grouping D-1199). It closes one register issue, `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` (`.agent/context/known-issues.yaml:5764`), under D-1201 A.
**Build Plan Section**: none. `docs/BUILD_PLAN.md` names neither the eval run book nor the describe capture, and row 6 found it byte-identical to row 0 (`edr-hub-audit.txt`: `BUILD_PLAN.md unchanged: True eval references: []`).
**Predecessor**: [2026-11-17-e2e-pointer-flakes-handoff.md](2026-11-17-e2e-pointer-flakes-handoff.md), Session 91, committed in `1ea63a1`. This session's `HEAD` and `baseline.sha` is `3e61b5b`, the 2026-11-18 triage commit that grouped Session 95 (`.agent/context/grouping/2026-11-18-eval-describe-session-grouping.md` §3). Session 95 is the only session of that grouping.

- **The capture (`RAW_CAPTURE`, `NO_OVERWRITE`, `NAMED_REFUSAL`, D-1201 A, D-1203, D-1204).**
  - `docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py` is new (LF, ASCII, 234 lines, 8,861 bytes), beside Session 64's `eval-run.md`.
  - `capture ROOT OUT` runs Session 64's `eval-harness.ts describe` in a subprocess: node on `mcp-server/node_modules/tsx/dist/cli.mjs`, from `mcp-server`, with no shell and with `ELECTRON_RUN_AS_NODE` removed from the child's environment. It writes the child's stdout bytes to `OUT` unchanged and its stderr to `OUT.stderr.txt`.
  - It refuses, with exit 1 and a named reason, an empty capture, a BOM, bytes that are not UTF-8, a CR byte, cp437 mojibake, a CUT count other than one, a failing harness and a timed-out one. A refused capture writes no `OUT` and keeps its bytes as `OUT.refused`.
  - It never overwrites: an existing `OUT`, `OUT.stderr.txt` or `OUT.refused` exits 2 before any child starts. A root outside Session 64's eval folder (`s64/eval` under `RECEIPTS_DIR`, the script's `BASE`) exits 2, and a missing `mcp-server/dist/index.js` exits 2 with "build first".
  - A write or close that fails after the exclusive create removes the file that call created and exits 2 with `error: OSError: ...`, so a failed capture leaves no partial `OUT`, `OUT.stderr.txt` or `OUT.refused` (`write_new`, the CVR round 1 correction for the execution review's F1).
  - `check FILE` runs the same refusals on a saved file.
- **One guard (`ONE_GUARD`, D-1201 A).** The script holds no pattern of its own. It loads `MOJIBAKE` and `CUT` from Session 92's `docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py` by path (`GUARD_PATH`), with bytecode writing off. A guard file that is missing or cannot load exits 2 with `error: guard not loaded:` and the path, with no traceback and no child started. `eval-rerun.py` is unchanged (RECORDS_KEPT, below).
- **The run book (`STEP3_NAMES_SCRIPT`).** `eval-run.md` gains a dated note after line 6, and step 3 (`:24` at row 0, now `:26`) runs `eval-describe.py capture` with a new root label and a receipt path that does not exist yet. The file went from 5,748 to 6,980 bytes, LF only (`edr-doc.txt`: `PASS exact-bytes: now 6980 B, expected 6980 B`, `PASS lf-only: CR bytes 0`). Session 64's `task.md`, plan and receipts are not touched.
- **The tests (D-1202).** `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py` is new (LF, ASCII, 440 lines, 29 tests, AC-1 to AC-7). It runs by path under pytest. Its SHA-256 `b581bcaac200f91a6565040b2cb054c7f72300c254c62fc7a9770782636682c8` was recorded at the CVR round 1 Red (the row-1 Red recorded `96a8d6b3922b325c7a00f06664182d44865209029fe48d7034898c76c58d6654`) and is unchanged at the CVR Green and in the gate.
- **Records (row 5, D-1205).** The issue is `resolved` through this plan's `issue-resolve.py`, bound to row 0's register hash. `known-issues.md` is rendered. Grouping row 95 (`:118`) reads `executed (Session 95)`.

**What Mat sees.**
- The next eval that follows `eval-run.md` step 3 gets a describe receipt with real arrows and en dashes, or a refusal that names what is wrong. It can no longer read cp437 mojibake into its prompts.
- Nothing else changes: no product code, no tool description, no app behaviour.

**Edges.**
- **The guard's stated limit.** The guard catches the cp437 reading only. Output decoded through another code page passes the `mojibake` check, and is caught by `cr` alone (the PowerShell redirect also writes CRLF). That limit is the plan's (§Spec Sufficiency, `edr95-expert-pass.txt`) and is not widened here.
- **The tie between the two plan folders (D-1201's cost).** Session 64's run book now depends on Session 92's folder. Moving or tidying either folder breaks step 3; the script then exits 2 and names the missing file, and never runs unguarded.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-18-eval-describe-raw-bytes/implementation-plan.md) §Single-statement contracts.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-18: "proceed with the next session prompt orchestration here like you did the others" (`implementation-plan.md:15`). `plan_to_exec_gate: human`. The plan review approved at round 1 with no findings (`.agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-plan-critical-review.md`, sha256 `174c848615186c5bc9ed74a32a206603d67a6c776e7ace698c3d21c35a792c4e`). The coordinator wrote that approval into the plan's Status line after the review, the only change since (Departures).

Receipts named by file name alone are in the session's receipts folder: the `eval-describe-raw-bytes` folder under `RECEIPTS_DIR`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | test | A clean UTF-8 receipt with real arrows and dashes and one CUT line passes `refusals`, and `check` exits 0 | Issue; grouping §3 | `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py:122` | ✅ |
| AC-2 | test | A cp437-decoded fixture is refused as `mojibake`, exit 1, in LF and in CRLF form (`cr` and `mojibake`) | Brief §Acceptance; grouping §3 | `test_eval_describe.py:135`, `:146` | ✅ |
| AC-3 | test | A real arrow beside a mojibake dash, and a real dash beside a mojibake arrow, are refused as `mojibake` | Brief §Acceptance | `test_eval_describe.py:160`, `:171` | ✅ |
| AC-4 | test | Empty, UTF-8 BOM, UTF-16 BOM, invalid UTF-8, bare CR, no CUT and two CUTs are each refused with their named reason | `NAMED_REFUSAL`; grouping §3 | `test_eval_describe.py:195-196` (seven cases) | ✅ |
| AC-5 | test | The guard is Session 92's, loaded by `GUARD_PATH`, with no second pattern in the script; a stub guard swapped in changes what is refused | `ONE_GUARD`; D-1201 | `test_eval_describe.py:212`, `:227` | ✅ |
| AC-6 | test | `capture` writes the child's stdout byte for byte and its stderr beside it; never overwrites; refuses a failing, a mojibake and a timed-out child with no `OUT`; refuses a root outside `BASE`; a write or close error after the exclusive create leaves no file (CVR round 1, F1) | `RAW_CAPTURE`; `NO_OVERWRITE` | `test_eval_describe.py:240`, `:254`, `:271`, `:282`, `:294`, `:309`, `:360` (four cases) | ✅ |
| AC-7 | test | Usage errors exit 2; a missing build exits 2 with "build first"; a missing or unloadable guard exits 2 with `error: guard not loaded:` and starts no child; every message is ASCII | Boundary Inventory | `test_eval_describe.py:386-387` (three cases), `:395`, `:407` | ✅ |
| AC-8 | reproduction | Both old-redirect forms, run by one `pwsh -NoProfile -File` run of `edr-old.ps1`, each give at least one `MOJIBAKE` match and exactly one CUT line; after Green, `check` refuses both receipts and Session 64's `s64-E1-describe.txt` with exit 1 and `mojibake` | Brief §Red first; issue verification | row 1 `edr-old-env.txt`, `edr-old-check.txt`; row 2 `edr-old-refused-e1.txt`, `edr-old-refused-step3.txt`, `edr-old-refused-s64.txt`; gate `edr-old-refused` | ✅ |
| AC-9 | live | `capture` on the real harness (root `s95-describe`) exits 0, and `edr-check.py live` passes against an independent `npx tsx` read on `s95-direct` | Brief §Acceptance; `RAW_CAPTURE` | row 3 `edr-capture.txt`, `edr-live.txt`; gate `edr-live-gate` | ✅ |
| AC-10 | doc | `eval-run.md` equals its row-0 bytes with the dated note and the new step 3, LF only, and `build()` still makes three prompts from it | `STEP3_NAMES_SCRIPT` | row 4 `edr-doc.txt`; gate `edr-doc` | ✅ |
| AC-11 | records | The nine record files keep their row-0 SHA-256, and both record selftests exit 0 (`edr-check.py records`) | `RECORDS_KEPT` | row 0 `edr-baseline.txt`; gate `edr-records` | ✅ |
| AC-12 | register | The issue is `resolved` through `issue-resolve.py` with a `verification` and `resolution_path` that cite the AC-8 and AC-9 receipts; `render` and `render --check` pass; grouping row 95 reads `executed (Session 95)` and no other grouping line changed | Brief §Acceptance; grouping §6 | row 5 `edr-issue-resolve.txt`, `edr-issues-render-check.txt`, `edr-register-check.txt`; gate `issues-render-check` | ✅ |
| AC-13 | gate | `session-gate.ps1` ends `session-gate: all steps exit 0` | Brief §Gate | H1-2 `edr-gate-h1.txt` | ✅ |
| Guard selftest (cross-ref) | records | Session 92's `eval-rerun.py --selftest` (`docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py:182`, its last line printed at `:252`): unchanged; run by `edr-check.py records` (`docs/execution/plans/2026-11-18-eval-describe-raw-bytes/edr-check.py:312-316`) and passes | Local Canon (`RECORDS_KEPT`) | row 0 `edr-baseline.txt`; gate `edr-records`: `eval-rerun selftest: ok` | ✅ |
| Checker selftest (cross-ref) | records | Session 64's `eval-check.py --selftest` (`docs/execution/plans/2026-11-11-capture-export-copy/eval-check.py:232`): unchanged; run by `edr-check.py records` (`edr-check.py:312-316`) and passes | Local Canon (`RECORDS_KEPT`) | row 0 `edr-baseline.txt`; gate `edr-records`: `eval-check selftest: 0 wrong` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1 | `AssertionError: eval-describe.py is not written yet: <the script's path>` (`edr-red.txt`, `25 failed in 0.35s`) | Row 2: `25 passed in 3.16s` (`edr-green.txt`) | `test_eval_describe.py:122` |
| AC-2 | the same assertion (`edr-red.txt`) | Row 2: `25 passed in 3.16s` (`edr-green.txt`) | `test_eval_describe.py:135`, `:146` |
| AC-3 | the same assertion (`edr-red.txt`) | Row 2: `25 passed in 3.16s` (`edr-green.txt`) | `test_eval_describe.py:160`, `:171` |
| AC-4 | the same assertion, seven cases (`edr-red.txt`) | Row 2: `25 passed in 3.16s` (`edr-green.txt`) | `test_eval_describe.py:195-196` |
| AC-5 | the same assertion (`edr-red.txt`) | Row 2: `25 passed in 3.16s` (`edr-green.txt`) | `test_eval_describe.py:212`, `:227` |
| AC-6 | the same assertion, six tests (`edr-red.txt`); CVR round 1: the new test's four cases, each `AssertionError: <file> survives the <write or close> failure` (`cvr1-red.txt`, `4 failed, 25 passed in 4.00s`) | Row 2: `25 passed in 3.16s` (`edr-green.txt`); CVR round 1: `29 passed in 4.65s` (`cvr1-green.txt`) | `test_eval_describe.py:240`, `:254`, `:271`, `:282`, `:294`, `:309`, `:360` |
| AC-7 | the same assertion, five tests (`edr-red.txt`) | Row 2: `25 passed in 3.16s` (`edr-green.txt`) | `test_eval_describe.py:386-387`, `:395`, `:407` |

- **Not in FAIL_TO_PASS:** AC-8 to AC-13 are checks (reproduction, live, doc, records, register and gate), not tests that failed at Red.
- **The Red.** Every one of the 25 tests failed by its first assertion, `SCRIPT.is_file()`, before the script existed (D-1202): `edr-red.txt` holds 25 `AssertionError: eval-describe.py is not written yet:` lines and ends `25 failed in 0.35s`, and `edr-red.txt.exit` reads `1`. `edr-red-check.txt`: `red-check: 1 receipt(s), 7 required test(s), 0 problem(s)` (`--require test_ac_1` to `--require test_ac_7`). The host load before the Red was 43.8 % (`edr-load-r1-red.txt`). The CVR round 1 Red, for one new test, is under **CVR round 1, F1** below.
- **The test file is unchanged from its last Red to Green.** Row 2, and after the CVR round 1 Red the gate's `edr-tests` step, compared its SHA-256 with `edr-test-sha.txt` (`test_sha256 <the file's hash> red <the recorded hash> equal: True`, `edr-D6-edr-tests.txt`).
- **Green ran with no skip.** Row 2's cell refuses a `skipped` line; the gate requires an `N passed in` line and no skipped, xfailed, xpassed or deselected test (`edr-D6-edr-tests.txt`: `pytest exit: 0 passed line: 29 passed in  skip found: False`).

#### Per-row evidence

**Row 0, baseline** (`edr-baseline.txt`)
- `baseline: all steps exit 0`; `anchor lines moved: none`.
- The S2 binding: the issue `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE`: `entries 1, status open, line 5764`; grouping row 95 `one proposed row: True`; the four `s95-*` roots `exists: False`; `tsx cli mcp-server/node_modules/tsx/dist/cli.mjs exists: True`.
- `check_home_path: ok files=2714 allowlisted=60 nul=31` (`edr-home-before.txt`).
- `edr-check.py records`: `PASS records-unchanged: changed []`, `eval-rerun selftest: ok`, `eval-check selftest: 0 wrong`.
- The selftests: `red-check selftest: 39 fixture(s) (13 positive, 26 negative), 0 wrong: []`; `eol-check selftest: 24 case(s), 0 wrong: []`; `identity selftest: 0 failure(s)`; `edr-check.py --selftest` `selftest: 0 failures`.
- **No moved citation (Session 51 RULE-3).** Every row-0 anchor was where the plan cites it (`anchor lines moved: none`), and the issue is still at `known-issues.yaml:5764` after the resolve. Step 3 of `eval-run.md` was at `:24` at row 0 and is at `:26` now, because row 4's note added two lines above it.

**Row 1, the old forms and the Red**
- The build: `npm --prefix mcp-server run build` after a 534 s wait for the host load at or below 50 %. `git status` showed no `mcp-server` path afterwards. It replaced `mcp-server/dist` with this tree's build; `dist/` is ignored (`.gitignore:17`).
- The shell (`edr-old-env.txt`): `psversion 7.6.10`, `psedition Core`, `console-output-codepage 437`, `output-encoding utf-8`, `e1-exit 0`, `step3-exit 0`.
- `edr-old-check.txt`:
  - the E-1 form (`rtk proxy npx tsx ... describe *>`, root `s95-old`, receipt `edr-old-e1.txt`): `e1: 37488 B`, `"moj_arrows": 9`, `"moj_dashes": 4`, `"mojibake": 13`, `"cut": 1`, no real arrow or dash; `old: e1 -> reproduced`;
  - the step-3 form (`npx tsx ... describe > f 2>&1`, root `s95-old3`, receipt `edr-old-step3.txt`): `step3: 37406 B` with the same counts; `old: step3 -> reproduced`;
  - `old: 2 of 2 forms reproduced, not []`.
- The Red: as above.

**Row 2, Green**
- `edr-green.txt`: `25 passed in 3.16s`.
- `check`, each exit 1:

  | Receipt | Refusal lines |
  |---|---|
  | `edr-old-e1.txt` | `cr: 835 CR byte(s)`; `mojibake: 14 match(es)` (`edr-old-refused-e1.txt`) |
  | `edr-old-step3.txt` | `cr: 834 CR byte(s)`; `mojibake: 13 match(es)` (`edr-old-refused-step3.txt`) |
  | `s64-E1-describe.txt` | `cr: 725 CR byte(s)`; `mojibake: 12 match(es)` (`edr-old-refused-s64.txt`) |

  `check` counts the whole file, so the E-1 form and Session 64's receipt each carry one more match than `edr-old-check.txt` counts: the `[rtk]` warning line that the redirect also decoded through cp437, at character offset 28 (the first match each refusal names). `edr-check.py old` drops `[rtk]` lines first. The plan's own count of Session 64's receipt is 9 arrows and 2 dashes, 11 matches without the `[rtk]` line and 12 with it (`edr-plan-bytes.txt`, `edr-plan-doc-probe.txt`). The new receipts carry 4 dashes, because the description Session 92 shipped holds more en dashes than Session 64's did.
- Ruff: `ruff format --check` and `ruff check` on both new files pass (`edr-green-fmt.txt`, `edr-green-lint.txt`).

**Row 3, live**
- `edr-capture.txt`: `captured: 36533 bytes sha256 6613cd4173b49d157a9232fa34ab3b057467f1a62b631441a712d30017176ccb`.
- `edr-live.txt`, against the direct read on `s95-direct` (`edr-direct.txt`):
  - `PASS equal-direct: receipt 36533 B, direct 36533 B`;
  - `PASS utf8: strict decode`; `PASS no-bom: first char checked`; `PASS no-cr: CR bytes 0`;
  - `PASS no-mojibake: MOJIBAKE matches 0`; `PASS no-moj-sequences: mojibake arrows and dashes 0`;
  - `PASS real-text: arrows 9, en dashes 4`; `PASS cut-once: CUT lines 1`;
  - `PASS tail-kept: '## avkit_convert action notes' after CUT and a final LF: True`;
  - `PASS cp437-trap: MOJIBAKE matches after a cp437 decode 13`;
  - `PASS build: 3 prompts, clean True`;
  - `PASS stderr-file: edr-describe.txt.stderr.txt`; `PASS no-refused: edr-describe.txt.refused`;
  - `edr-check: 13 pass, 0 fail []`.
- What the equality proves is narrow (plan AC-9): a second launcher and a second root give the same bytes, and a capture cut short yet clean would be caught. That `capture` leaves the bytes unchanged is AC-6's proof.

**Row 4, the run book**
- `edr-doc.txt`: `PASS exact-bytes: now 6980 B, expected 6980 B`; `PASS lf-only: CR bytes 0`; `PASS ascii-note: note and step 3`; `PASS build-new-text: 3 prompts`; `edr-check: 4 pass, 0 fail []`.
- `edr-eol-4.txt`: `eol docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md: LF, crlf 0, bare_lf 103, changed since row 0`; `eol-check: 11 scope path(s), 0 problem(s)`.

**Row 5, records** (`edr-issue-resolve.txt`)
- `decision logs read: 105 of 105`.
- `register sha256 before=b787fe3bb1d5aa3707015f72375766c0b8ab5fba3d6186bfca1867af4faac148`; `target sha256 after=49c130e9cddcba68bfbceb53ce620655cf151bb2e09464dfffb8bcde2e79c8bb CRLF=0 LF=5804`.
- `parsed fields changed: 4`: `.issues[145].resolution_path`, `.issues[145].status`, `.issues[145].verification.method` and `.issues[145].verification.result`.
- `issue-resolve: 0 problem(s)`.
- The render: `Rendered known-issues.md: 33 lines`, then `OK: known-issues.md is up-to-date` (`edr-issues-render.txt`, `edr-issues-render-check.txt`).
- `edr-register-check.txt`: `other issues changed: [] changed keys: ['resolution_path', 'status', 'verification'] issue ok: True grouping lines changed: [118] row ok: True`.
- The register before the resolve is kept as `issue-resolve/register-before-resolve.yaml`.

**Row 6, the hub** (`edr-hub-audit.txt`): `BUILD_PLAN.md unchanged: True eval references: []`.

**H1 rows**
- H1-1 (`task-unchecked.txt`): `unchecked implementation rows: []`.
- H1-3 (`edr-render-check.txt`): `Drift check passed — SSOT loaded (160 MEUs, 12 phases), rendered regions match on-disk content`.
- H1-4 (`skip-basis-check.txt`): `skip-basis changes since row 0: []`.
- H1-5 (`source-read-h1-5.txt`): `source-read: ok`.

**CVR round 1, F1** (the execution review, `2026-11-18-eval-describe-raw-bytes-implementation-critical-review.md`)
- **The finding.** `capture` created each file with exclusive create and wrote it in one `with` block, so a write or close that failed after the create left a partial file: an `OUT` cut short after the CUT line passed `check`, and `NO_OVERWRITE` then refused a retry.
- **The Red.** `test_ac_6_capture_write_failure_leaves_no_file` (`test_eval_describe.py:360`, four cases) swaps the module's `open` for one that fails on the target file only, after the CUT line or at close, with no harness. Against the unchanged script each case held exit 2 and `error: OSError:` and failed on the leftover file: `out.txt survives the write failure`, `out.txt survives the close failure`, `out.txt.stderr.txt survives the write failure`, `out.txt.refused survives the write failure`; `4 failed, 25 passed in 4.00s` (`cvr1-red.txt`, `cvr1-red.txt.exit` `1`). `cvr1-red-check.txt`: `red-check: 1 receipt(s), 1 required test(s), 0 problem(s)`. The host load before it was 46.2 % (`cvr1-load-red.txt`).
- **The Green.** `write_new(path, data)` in `eval-describe.py` creates the file with exclusive create, writes and closes it, and on any exception removes only that file and re-raises, so `main` prints `error: OSError: ...` and exits 2. All three writes use it; the existence check before the child and the messages are unchanged. `cvr1-green.txt`: `29 passed in 4.65s`; `cvr1-green-fmt.txt`: `2 files already formatted`; `cvr1-green-lint.txt`: `All checks passed!`.
- **The gate again.** The H1-2 cell ran a third time, unchanged, after one host-load wait (`host-load: 37.2 %` after 575 s, `cvr1-h1-2-driver.txt`): stamp `20261118-231019`, `session-gate: all steps exit 0`, with a fresh live capture of the same 36,533 bytes.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row0.ps1 (task.md row 0's Validation cell: baseline.ps1 records baseline.sha, the dirty list and hashes, the scope, skip and record hashes and the line-ending baseline, re-reads the anchors, the issue and grouping row 95, and runs the plan-local selftests); run twice, run 1 kept as edr-baseline-run1.txt; receipts edr-baseline.txt, edr-home-before.txt", "scope": "Row 0: the baseline at 3e61b5b, the S2 start condition, RECORDS_KEPT's first read and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3e61b5b (baseline.sha) plus row 0", "output": "edr-baseline-run1.txt: baseline step ruff-check-plan exit=1 (22 E501 in red-check.py; wrapped, then rerun). edr-baseline.txt: anchor lines moved: none; issue EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE entries 1, status open, line 5764; grouping row 95 one proposed row: True; the four s95 roots exists: False; tsx cli exists: True; PASS records-unchanged: changed []; eval-rerun selftest: ok; eval-check selftest: 0 wrong; red-check selftest: 39 fixture(s) (13 positive, 26 negative), 0 wrong: []; eol-check selftest: 24 case(s), 0 wrong: []; identity selftest: 0 failure(s); baseline: all steps exit 0. edr-home-before.txt: check_home_path: ok files=2714."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-1-build", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row1-build.ps1 (host-load.ps1, then rtk proxy npm --prefix mcp-server run build, then git status --porcelain -- mcp-server); receipts edr-load-r1-build.txt, edr-build.txt", "scope": "Row 1: the MCP build the harness needs (D-1203)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3e61b5b (baseline.sha) plus rows 0 and 1", "output": "edr-load-r1-build.txt: host-load: waited 534 s (bar 50 %); host-load: 50 %. edr-build.txt: avkit-mcp-server@0.1.0-rc.3 build, tsc -p tsconfig.json, exit 0. row1-build: mcp-server status empty."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-1-old-forms", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row1-old.ps1 (rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-18-eval-describe-raw-bytes/edr-old.ps1), then run-row1-validate.ps1 (host-load.ps1 and task.md row 1's Validation cell: edr-check.py old on both receipts); receipts edr-old-run.txt, edr-old-env.txt, edr-old-e1.txt, edr-old-step3.txt, edr-old-check.txt", "scope": "AC-8 first half: both old redirect forms reproduce the mojibake (S5)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3e61b5b (baseline.sha) plus rows 0 and 1", "output": "edr-old-env.txt: psversion 7.6.10; psedition Core; console-output-codepage 437; output-encoding utf-8; e1-exit 0; step3-exit 0. edr-old-check.txt: e1: 37488 B {\"arrows\": 0, \"cut\": 1, \"dashes\": 0, \"moj_arrows\": 9, \"moj_dashes\": 4, \"mojibake\": 13}; old: e1 -> reproduced; step3: 37406 B {\"arrows\": 0, \"cut\": 1, \"dashes\": 0, \"moj_arrows\": 9, \"moj_dashes\": 4, \"mojibake\": 13}; old: step3 -> reproduced; old: 2 of 2 forms reproduced, not []."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-1-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row1-validate.ps1 (task.md row 1's Validation cell, after the old-form check: pytest on docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py, its exit code kept, then red-check.py --require test_ac_1 to --require test_ac_7, and the test file's SHA-256 recorded); receipts edr-load-r1-red.txt, edr-red.txt, edr-red.txt.exit, edr-red-check.txt, edr-test-sha.txt", "scope": "AC-1 to AC-7 Red before eval-describe.py exists (D-1202)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3e61b5b (baseline.sha) plus rows 0 and 1", "output": "edr-load-r1-red.txt: host-load: 43.8 %. edr-red.txt: 25 lines AssertionError: eval-describe.py is not written yet: <the script's path>, each with where False = is_file(); 25 failed in 0.35s. edr-red.txt.exit: 1. edr-red-check.txt: red-check: 1 receipt(s), 7 required test(s), 0 problem(s). edr-test-sha.txt: 96a8d6b3922b325c7a00f06664182d44865209029fe48d7034898c76c58d6654."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-2-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row2.ps1 (task.md row 2's Validation cell: the test hash compared with edr-test-sha.txt, pytest on test_eval_describe.py, eval-describe.py check on the two old receipts and Session 64's s64-E1-describe.txt, ruff format --check and ruff check); receipts edr-green.txt, edr-old-refused-e1.txt, edr-old-refused-step3.txt, edr-old-refused-s64.txt, edr-green-fmt.txt, edr-green-lint.txt", "scope": "AC-1 to AC-7 Green; AC-8 second half: the three old receipts refused", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3e61b5b (baseline.sha) plus rows 0 to 2", "output": "edr-green.txt: 25 passed in 3.16s. edr-old-refused-e1.txt: cr: 835 CR byte(s); mojibake: 14 match(es), the first at character offset 28; exit 1. edr-old-refused-step3.txt: cr: 834 CR byte(s); mojibake: 13 match(es), the first at character offset 139; exit 1. edr-old-refused-s64.txt: cr: 725 CR byte(s); mojibake: 12 match(es), the first at character offset 28; exit 1. edr-green-fmt.txt: 2 files already formatted. edr-green-lint.txt: All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-3-live", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row3.ps1 (task.md row 3's Validation cell: eval-describe.py capture on root s95-describe, the direct npx tsx read on s95-direct, then edr-check.py live); receipts edr-capture.txt, edr-describe.txt, edr-direct.txt, edr-live.txt", "scope": "AC-9: the live capture on the real harness (RAW_CAPTURE, S10)", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3e61b5b (baseline.sha) plus rows 0 to 3", "output": "edr-capture.txt: captured: 36533 bytes sha256 6613cd4173b49d157a9232fa34ab3b057467f1a62b631441a712d30017176ccb. edr-live.txt: PASS equal-direct: receipt 36533 B, direct 36533 B; PASS utf8; PASS no-bom; PASS no-cr: CR bytes 0; PASS no-mojibake: MOJIBAKE matches 0; PASS no-moj-sequences: mojibake arrows and dashes 0; PASS real-text: arrows 9, en dashes 4; PASS cut-once: CUT lines 1; PASS tail-kept; PASS cp437-trap: MOJIBAKE matches after a cp437 decode 13; PASS build: 3 prompts, clean True; PASS stderr-file; PASS no-refused; edr-check: 13 pass, 0 fail []."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-4-doc", "command": "uv run python C:/Temp/av-kit/eval-describe-raw-bytes/edr-write-doc.py (eval-run.md from its row-0 copy with edr-check.py's NOTE and STEP3, as LF bytes); pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row4.ps1 (task.md row 4's Validation cell: edr-check.py doc, eol-check.py); receipts edr-write-doc.txt, edr-doc.txt, edr-eol-4.txt", "scope": "AC-10: the run book's note and step 3 (STEP3_NAMES_SCRIPT)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3e61b5b (baseline.sha) plus rows 0 to 4", "output": "edr-doc.txt: PASS exact-bytes: now 6980 B, expected 6980 B; PASS lf-only: CR bytes 0; PASS ascii-note: note and step 3; PASS build-new-text: 3 prompts; edr-check: 4 pass, 0 fail []. edr-eol-4.txt: eval-run.md: LF, crlf 0, bare_lf 103, changed since row 0; eol-check: 11 scope path(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-5-records", "command": "uv run python C:/Temp/av-kit/eval-describe-raw-bytes/edr-row5-prep.py (issue-resolve-set.json and grouping row 95 at :118, as LF bytes); pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row5.ps1 (task.md row 5's Validation cell: issue-resolve.py --expect-sha256 the row-0 register hash, issue_triage.py render and render --check, the register and grouping check); receipts edr-row5-prep.txt, edr-issue-resolve.txt, edr-issues-render.txt, edr-issues-render-check.txt, edr-register-check.txt", "scope": "AC-12: the issue resolved, the render and grouping row 95 (D-1205)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3e61b5b (baseline.sha) plus rows 0 to 5", "output": "edr-issue-resolve.txt: decision logs read: 105 of 105; register sha256 before=b787fe3bb1d5aa3707015f72375766c0b8ab5fba3d6186bfca1867af4faac148; target sha256 after=49c130e9cddcba68bfbceb53ce620655cf151bb2e09464dfffb8bcde2e79c8bb CRLF=0 LF=5804; parsed fields changed: 4 (.issues[145].resolution_path, .status, .verification.method, .verification.result); issue-resolve: 0 problem(s). edr-issues-render.txt: Rendered known-issues.md: 33 lines. edr-issues-render-check.txt: OK: known-issues.md is up-to-date. edr-register-check.txt: other issues changed: [] changed keys: ['resolution_path', 'status', 'verification'] issue ok: True grouping lines changed: [118] row ok: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-6-h1-1-hub", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row-6.ps1 (task.md row 6's Validation cell); pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row-H1-1.ps1 (task.md row H1-1's Validation cell); receipts edr-hub-audit.txt, task-unchecked.txt", "scope": "Row 6 (the build plan hub) and H1-1 (no unchecked implementation row)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3e61b5b (baseline.sha) plus rows 0 to 6 and H1-1", "output": "edr-hub-audit.txt: BUILD_PLAN.md unchanged: True eval references: []. task-unchecked.txt: unchecked implementation rows: []."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-h1-2-gate-run1", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row-H1-2.ps1 (task.md row H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-18-eval-describe-raw-bytes/session-gate.ps1), first run, stamp 20261118-215027; receipts kept in the gate-run1 folder: edr-gate-h1.txt and edr-D6-<step>.txt", "scope": "H1-2 first run: stopped at the host-load step; superseded by edr-h1-2-session-gate", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6d01feb34875b1e3fc9d707e4ce43504ea2e6ea152ca1eb26b49abdaaa34d455", "output": "edr-gate-h1.txt (gate-run1): every step from identity-before to edr-old-refused exit=0; host-load exit=1: host-load: still above the 50 % bar after 619 s; host-load: 79.6 %; mcp-build, edr-live-gate, issues-render-check, state-render and identity-after not_run. The load was from programs outside this session."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-h1-3-h1-5-closeout", "command": "uv run python C:/Temp/av-kit/eval-describe-raw-bytes/edr-focus-insert.py (the Session 95 entry on top of .agent/context/current-focus.md, by bytes, CRLF kept, refused if a 'Current priority: Session 95' line exists); pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row-H1-3.ps1 (rtk proxy uv run python tools/meu_status.py render --check); pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row-H1-4.ps1 (task.md row H1-4's skip-basis check); uv run python C:/Temp/av-kit/eval-describe-raw-bytes/source-read.py (H1-5); receipts edr-focus-insert.txt, edr-render-check.txt, skip-basis-check.txt, source-read-h1-5.txt", "scope": "H1-3 (current focus and the state render), H1-4 (the skip basis, S9) and H1-5 (the template and exemplar read)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state plus H1-3's current-focus entry (current-focus.md is outside identity.py's inputs)", "output": "edr-focus-insert.txt: before: 93950 B CRLF 230; after: 95400 B CRLF 233 bare LF 0; tail kept: True; session 95 prefix lines: 1; focus-insert: ok. edr-render-check.txt: Drift check passed - SSOT loaded (160 MEUs, 12 phases), rendered regions match on-disk content. skip-basis-check.txt: skip-basis changes since row 0: []. source-read-h1-5.txt: TEMPLATE.md 6703 B, 2026-11-17-e2e-pointer-flakes-handoff.md 48377 B (newest by mtime), 2026-11-17-mcp-audit-refresh-handoff.md 58804 B; source-read: ok."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-cvr1-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-cvr1-red.ps1 (host-load.ps1 up to 9 tries; the test file's SHA-256 written to cvr1-test-sha.txt; rtk proxy uv run pytest docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py --tb=short -q -rs -p no:cacheprovider, its exit code kept in cvr1-red.txt.exit; then red-check.py --require test_ac_6_capture_write_failure_leaves_no_file); before it, ruff format --check and ruff check on the test file; receipts cvr1-load-red.txt, cvr1-test-sha.txt, cvr1-red.txt, cvr1-red.txt.exit, cvr1-red-check.txt, cvr1-red-fmt.txt, cvr1-red-lint.txt", "scope": "CVR round 1, F1 (AC-6, RAW_CAPTURE): the new regression test against the unchanged eval-describe.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 gate run 2 state plus the CVR round 1 regression test", "output": "cvr1-load-red.txt: host-load: 46.2 %. cvr1-red-fmt.txt: 1 file already formatted. cvr1-red-lint.txt: All checks passed! cvr1-test-sha.txt: b581bcaac200f91a6565040b2cb054c7f72300c254c62fc7a9770782636682c8. cvr1-red.txt: test_ac_6_capture_write_failure_leaves_no_file[out-write] AssertionError: out.txt survives the write failure; [out-close] AssertionError: out.txt survives the close failure; [stderr-write] AssertionError: out.txt.stderr.txt survives the write failure; [refused-write] AssertionError: out.txt.refused survives the write failure; each after exit 2 and error: OSError: held; 4 failed, 25 passed in 4.00s. cvr1-red.txt.exit: 1. cvr1-red-check.txt: red-check: 1 receipt(s), 1 required test(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-cvr1-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-cvr1-green.ps1 (rtk proxy uv run pytest docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py --tb=short -q -rs -p no:cacheprovider; rtk proxy uv run ruff format --check and ruff check on docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py and the test file); receipts cvr1-green.txt, cvr1-green.txt.exit, cvr1-green-fmt.txt, cvr1-green-lint.txt, cvr1-green-driver.txt", "scope": "CVR round 1, F1: write_new in eval-describe.py; the full test file Green", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "output": "cvr1-green.txt: 29 passed in 4.65s. cvr1-green-fmt.txt: 2 files already formatted. cvr1-green-lint.txt: All checks passed! cvr1-green-driver.txt: cvr1-green: pytest 0, format 0, lint 0."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "edr-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-h1-2-rerun.ps1 (host-load.ps1 up to 9 tries, then pwsh -NoProfile -File C:/Temp/av-kit/eval-describe-raw-bytes/run-row-H1-2.ps1, task.md row H1-2's Validation cell unchanged: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-18-eval-describe-raw-bytes/session-gate.ps1 *> C:/Temp/av-kit/eval-describe-raw-bytes/edr-gate-h1.txt); step receipts edr-D6-<step>.txt; driver cvr1-h1-2-driver.txt; third run, after the CVR round 1 correction", "scope": "H1-2 and AC-13: the session gate from identity-before to identity-after: task-contract, scope-paths, line-endings, home-path, three selftests, py-format, py-lint, edr-tests, edr-records, edr-doc, edr-old-refused, host-load, mcp-build, edr-live-gate, issues-render-check and state-render", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224", "output": "cvr1-h1-2-driver.txt: wait try 1: host-load exit 0 at 23:10:19 (host-load: waited 575 s, 37.2 %); H1-2 cell exit 0 at 23:10:50. edr-gate-h1.txt: gate stamp: 20261118-231019; every run step exit=0; skipped with reasons: py-tests, py-types, ui-types/ui-lint/ui-tests/ui-build/ui-electron, mcp-types/mcp-tests and openapi (every packages/, tools/, ui/, tests/ and server file keeps its baseline-skip-hashes.json hash, H1-4) and mcp-audit (no server file changes; a network run); tested_state before and after equal; session-gate: all steps exit 0. edr-D6-task-contract.txt: OK: 24 row(s); 2 row(s) exempt (view_file): H1-5, H2-1. edr-D6-scope-paths.txt: changed paths: 28 outside scope: []; read-never-changed files: 10 mismatch: [] baseline-dirty hash mismatch: []; foreign class (coordinator, printed only): 8 changed: [] row-0 hash moved: []; head moved (S4): False. edr-D6-line-endings.txt: eol-check: 11 scope path(s), 0 problem(s). edr-D6-home-path.txt: check_home_path: ok files=2719. edr-D6-py-format.txt: 7 files already formatted. edr-D6-py-lint.txt: All checks passed! edr-D6-edr-tests.txt: test_sha256 b581bcaac200f91a6565040b2cb054c7f72300c254c62fc7a9770782636682c8 red b581bcaac200f91a6565040b2cb054c7f72300c254c62fc7a9770782636682c8 equal: True; 29 passed in 3.01s; skip found: False. edr-D6-edr-records.txt: edr-check: 3 pass, 0 fail []. edr-D6-edr-doc.txt: edr-check: 4 pass, 0 fail []. edr-D6-edr-old-refused.txt: edr-old-refused: ok, 3 of 3 refused. edr-D6-host-load.txt: samples [22, 51, 17, 50, 34] mean=34.8; host-load: 34.8 %. edr-D6-mcp-build.txt: exit 0. edr-D6-edr-live-gate.txt: captured: 36533 bytes sha256 6613cd4173b49d157a9232fa34ab3b057467f1a62b631441a712d30017176ccb; edr-check: 13 pass, 0 fail []. edr-D6-issues-render-check.txt: OK: known-issues.md is up-to-date. edr-D6-state-render.txt: Drift check passed. edr-D6-identity-after.txt: tested_state 3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224."}
```

### Quality Gate Results

| Step | Result (receipt) |
|------|------------------|
| Gate | `session-gate: all steps exit 0` (`edr-gate-h1.txt`, stamp `20261118-231019`, the third run, after the CVR round 1 correction); every run step `exit=0` |
| Identity | `tested_state 3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224`, equal before and after (`edr-D6-identity-before.txt`, `edr-D6-identity-after.txt`) |
| Task contract | `OK: 24 row(s)`; `2 row(s) exempt (view_file): H1-5, H2-1` (`edr-D6-task-contract.txt`) |
| Scope | `changed paths: 28 outside scope: []`; `read-never-changed files: 10 mismatch: [] baseline-dirty hash mismatch: []`; `foreign class (coordinator, printed only): 8 changed: [] row-0 hash moved: []`; `head moved (S4): False` (`edr-D6-scope-paths.txt`) |
| Line endings | `eol-check: 11 scope path(s), 0 problem(s)` (`edr-D6-line-endings.txt`) |
| Home path | `check_home_path: ok files=2719 allowlisted=60 nul=31` (`edr-D6-home-path.txt`) |
| Selftests | red-check `39 fixture(s) (13 positive, 26 negative), 0 wrong`; eol-check `24 case(s), 0 wrong`; edr-check `selftest: 0 failures` (`edr-D6-red-check-selftest.txt`, `edr-D6-eol-check-selftest.txt`, `edr-D6-edr-check-selftest.txt`) |
| Ruff | `7 files already formatted`; `All checks passed!` (`edr-D6-py-format.txt`, `edr-D6-py-lint.txt`) |
| Tests | `29 passed in 3.01s`; the test file's hash equals the CVR round 1 Red's; `skip found: False` (`edr-D6-edr-tests.txt`) |
| Records | `PASS records-unchanged: changed []`; `eval-rerun selftest: ok`; `eval-check selftest: 0 wrong`; `edr-check: 3 pass, 0 fail []` (`edr-D6-edr-records.txt`) |
| Run book | `edr-check: 4 pass, 0 fail []` (`edr-D6-edr-doc.txt`) |
| Old receipts | `edr-old-refused: ok, 3 of 3 refused` (`edr-D6-edr-old-refused.txt`) |
| Host load | samples `[22, 51, 17, 50, 34]`, `mean=34.8`, `host-load: 34.8 %` (`edr-D6-host-load.txt`) |
| MCP build | exit 0 (`edr-D6-mcp-build.txt`) |
| Live | `captured: 36533 bytes sha256 6613cd4173b49d157a9232fa34ab3b057467f1a62b631441a712d30017176ccb`, the same bytes as row 3; `edr-check: 13 pass, 0 fail []` against the gate's own direct read (`edr-D6-edr-live-gate.txt`) |
| Registers | `OK: known-issues.md is up-to-date` (`edr-D6-issues-render-check.txt`); the state render's drift check passed (`edr-D6-state-render.txt`) |
| Skipped | `py-tests`, `py-types`, `ui-types/ui-lint/ui-tests/ui-build/ui-electron`, `mcp-types/mcp-tests`, `openapi`: every file under `packages/`, `tools/`, `ui/`, `tests/` and the server keeps its row-0 hash (H1-4); `mcp-audit`: no server file changes, and it is a network run |
| Gate run 1 | stamp `20261118-215027`: `host-load: still above the 50 % bar after 619 s`, `host-load: 79.6 %`; later steps `not_run` (the `gate-run1` folder) |
| Gate run 2 | stamp `20261118-223126`: `session-gate: all steps exit 0` at `tested_state 3e61b5ba074c9434ca7ea1bea9d809da80305560+6d01feb34875b1e3fc9d707e4ce43504ea2e6ea152ca1eb26b49abdaaa34d455`; superseded when the CVR round 1 correction changed `eval-describe.py` and the test file (the `gate-run2` folder) |

---

## Changed Files

Counts are added and removed lines against `HEAD` `3e61b5b` (`git diff --numstat --ignore-cr-at-eol`). A new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step, `edr-D6-line-endings.txt`).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py` | new: `RAW_CAPTURE`, `ONE_GUARD`, `NAMED_REFUSAL`, `NO_OVERWRITE` (row 2); `write_new` (CVR round 1, F1) | 234 lines | LF |
| `docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md` | the dated note after `:6`; step 3 (`STEP3_NAMES_SCRIPT`, row 4) | +3 / -1 | LF kept |
| `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py` | new: AC-1 to AC-7 (row 1); the F1 regression test (CVR round 1) | 440 lines | LF |
| `.agent/context/known-issues.yaml` | the issue resolved (`issue-resolve.py`, row 5) | +4 / -3 | LF kept |
| `.agent/context/known-issues.md` | `issue_triage.py render` (row 5) | +3 / -4 | LF |
| `.agent/context/grouping/2026-11-18-eval-describe-session-grouping.md` | row 95 (`:118`): `executed (Session 95)` (row 5) | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 95 entry (H1-3) | +3 / -0 | CRLF kept |
| `.agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-handoff.md` | this handoff (H1-6) | new | LF |
| `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/` | the plan and task (row marks), the plan-time scripts (`edr-check.py`, `edr-old.ps1`), the row-0 copies (`red-check.py`, `identity.py`, `eol-check.py`, `issue-resolve.py`, `host-load.ps1`), `baseline.ps1` and its records, and `session-gate.ps1` | new folder | LF |

**Read, never changed** (`RECORDS_KEPT`): `eval-rerun.py` and `capture-description.expected.txt` in Session 92's folder; Session 64's `eval-check.py`, `eval-harness.ts`, `eval-seed.py`, `task.md` and `implementation-plan.md`; `mcp-server/scripts/audit/backend.ts`; Session 64's receipt `s64-E1-describe.txt` in `RECEIPTS_DIR`; and `docs/BUILD_PLAN.md`. Each keeps its row-0 SHA-256: the gate's `edr-records` step reads `PASS records-unchanged: changed []`, and its `scope-paths` step reads `read-never-changed files: 10 mismatch: []` (`edr-D6-edr-records.txt`, `edr-D6-scope-paths.txt`).

**The foreign class** (`.agent/model-registry.local.json`, `.claude/agents/*.md`, `.cursor/agents/*.md`) belongs to the coordinator. None of its 8 files changed during the session: `foreign class (coordinator, printed only): 8 changed: [] row-0 hash moved: []` (`edr-D6-scope-paths.txt`).

**Ignored files this session left behind** (not in `git status`):
- `mcp-server/dist/`, rebuilt by row 1 and by the gate's `mcp-build` step (`.gitignore:17`).
- Session 92's folder holds `__pycache__/eval-rerun.cpython-312.pyc`, dated 2026-11-18 20:27, written by a plan-time load before the plan turned bytecode writing off. It is left in place. Session 64's folder holds an older `__pycache__/eval-check.cpython-312.pyc` (2026-11-11), not from this session, also left.

Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | no | behavior | AC-6 / `RAW_CAPTURE`: a write or close error after the exclusive create left a partial file (round 1 injected ENOSPC and found 23,154 of the child's 36,533 bytes kept, which `check` accepted). Corrected by `write_new` for all three writes, with four Red then Green regression cases (CVR round 1). | `docs/execution/plans/2026-11-11-capture-export-copy/eval-describe.py:143`; `docs/execution/plans/2026-11-18-eval-describe-raw-bytes/test_eval_describe.py:360` | Keep these regressions. | fixed |

- **The loop.** Ledger `edr-execution-2026-11-18-eval-describe-raw-bytes`, 2 of 6 rounds used, reviewer `codex-independent-reviewer`, dispatched by the coordinator.
  - Round 1: `changes_required`, one finding (F1, blocking at that round), `intent_achieved=partial` (dispatch receipts `C:/Temp/av-kit/dispatch/edr-exec-r1/`, console `edr-exec-console-r1.txt`).
  - Round 2: `approved`, F1 `open` to `fixed`, no new findings, `intent_achieved=yes` (`C:/Temp/av-kit/dispatch/edr-exec-r2/`, console `edr-exec-console-r2.txt`).
- **The canonical review.** `.agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-implementation-critical-review.md`, rolling, at round 2; byte-identical to `C:/Temp/av-kit/edr-exec-review-round-2.md` (33,195 B, SHA-256 `d105cbbe1eca7af1012d03736f31f5dc0eda16094adf5e70aade6a44ae017115`).
- **The reviewer's own checks (round 2).** The four F1 cases passed; its fault probe found 6 write/close cleanups, 3 competing creates preserved and 3 preexisting paths that never reached the child; its audit, run book, records and identity checks passed.
- **A sandbox limit, not a finding.** The reviewer's full local pytest read `1 failed, 28 passed in 34.11s`: only `test_ac_6_capture_refuses_timeout` (32.08 s against `< 30`), because `taskkill` is denied in its sandbox, as in round 1. The gate's own run reads `29 passed` (`edr-D6-edr-tests.txt`).
- **Receipts.** H1-7a: `OK: review_mode=execution; round 2 of 6; verdict=approved; open findings=0` (`review-state-check.txt`, `review-state.json`). H1-7b: `OK: approved at round 2 of 6, 0 open blocking findings` (`exec-review.txt`).

### Verdict

`approved` at round 2 of 6: F1 fixed, no new findings. The reviewer's `tested_state` `3e61b5ba074c9434ca7ea1bea9d809da80305560+6b40c5149bf6e2f9f85afdcd4f1f1ba8e52150e6f131b66e1299985af6403224` equals the gate run 3 value.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Mojibake from a code page other than cp437 | out-of-scope | — | The guard's stated limit (plan §Spec Sufficiency); such output is still refused by `cr` |
| Steps 1 and 4 of `eval-run.md` (the `seed` and `call` redirects) | out-of-scope | — | Plan §Out of Scope: their receipts are logs no model reads |
| An eval rerun on the clean surface | out-of-scope | — | Plan §Out of Scope; grouping §3 Gate |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |

### Departures and their basis

- **The plan and task hashes.** The plan's sha256 moved from the reviewed `78d24c0b29874de0d4eb4ba0e0e481a8341f3ad17fa95d72ec5a0d3d5f67a269` to `83a3cdcd3407684740b5e8b522fb02c9f89795e558d934bfac7e544c2803f2b2` when the coordinator wrote the execution approval into the Status line (`implementation-plan.md:15`); the coordinator's brief states that line is the only change after the review. No execution decision was added, so the plan is still at that hash. task.md was `51c158bc2f62ef63c159aa537aedefceffb1c2db78b35bb1df7e0ccf5aa7ec48` at row 0 and has changed only by its row marks. Neither file is an `identity.py` input.
- **Row 0 ran twice.** The first run (`edr-baseline-run1.txt`, kept) stopped at `baseline step ruff-check-plan exit=1`: `ruff check` found 22 E501 lines in `red-check.py` as copied from Session 83. The 22 lines were wrapped (formatting only; its selftest still reads `39 fixture(s) ... 0 wrong`), and row 0 was run again. On the rerun, `baseline-records.json` already existed from run 1, so the records step compared instead of recording (`baseline records: baseline-records.json exists from an earlier run of this row; comparing`, then `PASS records-unchanged: changed []`). The host load at row 0 was recorded (94.8 %), not waited on; row 0 has no build, Red or gate.
- **The session gate's shape.** `session-gate.ps1` is Session 92's gate adapted to this plan's §Session gate table, written at H1-2. Its `edr-old-refused` step requires exit 1 and a non-zero count, `mojibake: [1-9][0-9]* match`, for each of the three receipts, which is stricter than row 2's cell (the word `mojibake`). Before the run, a wiring probe compiled each of the gate's inline Python checks and dry-ran the scope check (exit 0), and a parse check found 0 parse errors and that `rtk proxy` passes a child's exit code through.
- **The gate ran twice.** The first run (stamp `20261118-215027`) passed every step up to `edr-old-refused` and stopped at `host-load`: `host-load: still above the 50 % bar after 619 s`, `host-load: 79.6 %`, with `mcp-build`, `edr-live-gate`, `issues-render-check`, `state-render` and `identity-after` `not_run`. The load came from programs outside this session. Its receipts are kept in the `gate-run1` folder. After a further wait (a second wait also failed, `host-load: 93.8 %` after 620 s, `edr-load-h1-2-run2.txt`; the rerun's first wait failed and its second read `host-load: 39.6 %` after 532 s, `edr-h1-2-rerun-driver.txt`), the H1-2 cell ran again unchanged; that second run (stamp `20261118-223126`) was the gate of record until the CVR round 1 correction, after which a third run (stamp `20261118-231019`) is. Run 2's receipts are kept in the `gate-run2` folder.
- **Scratch scripts.** Each row's Validation cell was copied verbatim into a `.ps1` file after an environment header and run with `pwsh -NoProfile -File`. The edits rows name were made by byte-level Python scripts in the receipts folder, which keep each file's line endings. Three of those scripts were reformatted by `ruff format` after they had run (formatting only).
- **CVR round 1 (F1).** The execution review's F1 (`RAW_CAPTURE`: a write or close failure left a partial file) was corrected Red first: the regression test `test_ac_6_capture_write_failure_leaves_no_file` failed by assertion (`cvr1-red.txt`, `cvr1-red-check.txt`), then `write_new` made it pass (`cvr1-green.txt`), and the gate ran again (`cvr1-h1-2-driver.txt`). What that moved:
  - **The Red hash receipt.** The gate's `edr-tests` step compares the test file with `edr-test-sha.txt`, so that receipt now holds the CVR Red's hash `b581bcaac200f91a6565040b2cb054c7f72300c254c62fc7a9770782636682c8` (`cvr1-test-sha.txt`); the row-1 receipt (`96a8d6b3922b325c7a00f06664182d44865209029fe48d7034898c76c58d6654`) is kept as `cvr1-edr-test-sha-row1.txt`. `session-gate.ps1` is unchanged.
  - **The gate record.** Gate run 2's evidence record would no longer match `tested_state`, so the `edr-h1-2-session-gate` record now holds run 3; run 2 is kept as a Quality Gate row and its receipts in the `gate-run2` folder.
  - **Rows.** No task row was unmarked or re-marked: H1-2, H1-6, H1-6a and H1-6b ran again with their cells unchanged, and their receipts were overwritten in place (run 2's gate receipts copied first).
  - **current-focus.md (a coordinator edit).** The CVR left `current-focus.md` out of its file scope. Before the round 2 review, the coordinator changed the Session 95 entry from `25 tests pass` to `29 tests pass (4 added for the round-1 review finding F1, a failed write leaving a partial file)`, keeping CRLF, and told the reviewer, who accepted it (its audit: `focus 233 CRLF`). Measured after the review by bytes: 95,483 B, 233 CRLF, no bare LF, the new phrase present and `25 tests` absent. This session did not write that change.
- **Execution decisions.** None was needed: D-1207 to D-1210 are unused. D-1201 to D-1206 are the plan's, so the Decision Log below is `None.`.

### Execution notes

- **The decisions.**

  | Id | What was decided |
  |---|---|
  | D-1201 | A: `eval-describe.py` beside `eval-run.md` imports Session 92's guard; handed to the agent under Mat's 2026-11-18 words, `mandatory: none`. |
  | D-1202 | The tests are a pytest file in this plan folder, run by path; each asserts the script exists first. |
  | D-1203 | Node runs tsx's CLI on the harness with no shell; "build first" when `dist/index.js` is missing. |
  | D-1204 | Never overwrite; new `s95-*` roots; Session 64's roots and receipts kept. |
  | D-1205 | The register is updated by `issue-resolve.py`, bound to the row-0 hash. |
  | D-1206 | The Red asserts both old forms, run in one `pwsh -NoProfile -File` script. |

- **Processes.** No row started the desktop app or called, started or stopped the avkit MCP server that the IDE runs. The harness started and stopped its own backend over the `s95-*` scratch roots. No process was stopped by this session.
- **Data.** No row read inside an eval root, Mat's app data, settings, downloads or models. No model call, eval run or network use.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 to H1-5 |
| CVR round 1 | 2026-11-18 | claude-code-local (Claude Opus 5.5) | F1 corrected (`write_new`, the regression test, Red then Green); gate run 3, stamp `20261118-231019` |
| Execution review | 2026-11-18 | codex-independent-reviewer (dispatched by the coordinator) | Round 1 `changes_required` (F1); round 2 `approved`, F1 fixed, no new findings |
| Codex Validation Report | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Report filled from the round 2 review; H1-7 to H1-7b marked; the coordinator's `current-focus.md` edit recorded |
