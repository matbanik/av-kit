---
date: "2026-11-17"
project: "2026-11-17-mcp-audit-refresh"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-17-mcp-audit-refresh/implementation-plan.md"
build_plan_section: "none (audit and tool-description debt; no MEU, D-1155)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-17-tts-fp16-guard-ship-MEU-144-handoff.md"
---

# Handoff: 2026-11-17-mcp-audit-refresh-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. Session 92 is audit and tool-description debt with no MEU (D-1155), as Sessions 78, 79 and 90 were. It closes three register issues: `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT`, `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` (Mat's D-1134 A) and `MCP-AUDIT-BASELINE-PENDING-CROP`, and registers one new issue, `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` (D-1163).
**Build Plan Section**: none. `docs/build-plan/05-mcp-server.md` gains one paragraph on the capture description.
**Predecessor**: [2026-11-17-tts-fp16-guard-ship-MEU-144-handoff.md](2026-11-17-tts-fp16-guard-ship-MEU-144-handoff.md), Session 74, committed as `cba97fe`, which is this session's `HEAD` and `baseline.sha`. Session 92 is from the 2026-11-17 value triage grouping (`.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` §3). It ran on the coordinator's dispatch while Session 91's plan was still uncommitted, though the plan's Status line puts Session 91 first. Session 91's files share no path with this session's scope.

- **The census proof (`NETWORK_PROOF_SAMPLE`, `PROBES_SEAM`, `NETWORK_PROOF_GATHER`, `FORBIDDEN_IMPORTS_KEPT`, D-1156, D-1160).**
  - `mcp-server/scripts/audit/network-proof.ts` is new (LF, 161 lines). It exports `NETWORK_PROOF_SAMPLES = 3`, `NETWORK_PROOF_GAP_MS = 5000`, `sampleBlocked`, the `NetworkProbes` type, `REAL_PROBES` and `gatherNetworkProof`.
  - `REAL_PROBES` holds the three probes moved from `run.ts` with their Python code, `cwd`, encoding and 180 s timeout unchanged. Its `sleep` blocks synchronously (`Atomics.wait`).
  - In container mode, each URL's direct fetch is now tried up to 3 times, about 5 s apart, and the proof holds when any try is blocked. Authoritative mode gathers no proof, as before.
  - `run.ts` replaces the row-0 census block (`:547-577`) with one `gatherNetworkProof({ ..., probes: REAL_PROBES })` call. It drops the three moved functions and the `NETWORK_STEP_URLS` import. `AuditDeps` is unchanged.
  - The new file holds none of the forbidden import strings.
- **The workflow note (`WORKFLOW_NOTE`).** `.agent/workflows/mcp-audit.md` gains one nested line after `:20`, under step 3's Container bullet (CRLF kept). It says that each proof is tried up to 3 times and holds when any try is blocked, and that a still-counted network member gets one container rerun before it is filed.
- **The `avkit_capture` description (`CAPTURE_TOOL_DESCRIPTION`, `DESC_SHAPE`, `DESC_TRACE`, `DESC_PIN`, D-1134 A, D-1157).**
  - `capture.ts` exports `CAPTURE_TOOL_DESCRIPTION`, composed from the constants `captureDescriptions` already used. It equals `capture-description.expected.txt` byte for byte: 3,981 characters in 14 lines (`mar-desc-check.txt`).
  - Line 1 is the lead: call `image` to view a frame or sheet; call `sheet` again over a narrower span to zoom.
  - Lines 2 to 5 carry the `Workflow:`, `Prerequisite:`, `Returns:` and `Errors:` markers once each.
  - Lines 6 to 14 hold one line per action, in `ACTION_INDEX` order, and each sentence on them is in that action's `_meta` text.
  - `registry.ts` changes `:17` (the import) and `:172` (`avkit_capture: CAPTURE_TOOL_DESCRIPTION,`).
  - What stays byte-identical to row 0's record:
    - `captureDescriptions`;
    - every tool's `_meta.action_descriptions`;
    - every input schema;
    - the other seven top-level descriptions.
  - `05-mcp-server.md` gains the planned paragraph after `:103` (CRLF kept).
- **The eval (`EVAL_RERUN`, D-1158, D-1186).**
  - The coordinator ran the three Session 64 tasks, one fresh Claude Haiku subagent per task, on the new real surface. All three passed `eval-rerun.py check`.
  - The first describe receipt and its prompts held cp437 mojibake. Under D-1186 they were re-captured as raw bytes before any subagent ran (Departures).
- **The baseline (`AUDIT_RUN`, `AUDIT_TMP`, `BASELINE_RECORD`, `PENDING_EMPTIED`, D-1159 A).**
  - One authoritative audit ran at `cba97fe` with `--update-baseline` and the committed report path: 104/104 pass, 0 discovery findings, cleanup ok.
  - The run recorded five keys in `baseline-snapshot.json` (now LF, 75 entries) and in the report: `avkit_convert.probe`, `avkit_capture.crop`, `avkit_capture.frames`, `avkit_capture.sheet` and `avkit_capture.export`.
  - `coverage.test.ts` holds an empty `BASELINE_PENDING`, through the four §Test pins edits (Changed Files).
- **Records (row 8).**
  - The three issues are resolved through `issue-resolve.py`, bound to row 0's register hash, with their `meu_links` kept.
  - `known-issues.md` is rendered.
  - Grouping row 92 (`:164`) reads `executed (Session 92)`.
  - D-1163 added `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` after the row's check (Departures).

**What Mat sees.**
- A model that loads av-kit's tools upfront now reads, in `avkit_capture`'s description:
  - call `image` to view a frame or sheet;
  - call `sheet` again over a narrower span to zoom;
  - one line per action.
- The other seven tools read as before.
- The IDE's avkit server keeps the old text until it restarts. No row started, stopped or called it, but the build rewrote `mcp-server/dist/`, which it loads at its next start.
- A container audit on a flaky network retries each network proof up to three times before it counts a failure.
- The committed audit baseline and report record convert probe, crop, frames, sheet and export as passing on this host.

**Edges.**
- A network URL costs up to three probe runs (each with a 180 s timeout) plus two 5 s gaps, in container mode only.
- Three eval runs at one per task can still pass by chance. That is the measure Mat chose (D-1134 A, D-1158).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-17-mcp-audit-refresh/implementation-plan.md) §Single-statement contracts.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-17: "orchestrate the plan creation for all sessions and proceed with execution for each" (`implementation-plan.md:15`). `plan_to_exec_gate: human`. The plan review approved at round 1 (`.agent/context/handoffs/2026-11-17-mcp-audit-refresh-plan-critical-review.md`). Mat ruled D-1159 A on 2026-11-18.

Receipts named by file name alone are in the session's receipts folder: the `mcp-audit-refresh` folder under `RECEIPTS_DIR`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | unit | `NETWORK_PROOF_SAMPLES === 3`, `NETWORK_PROOF_GAP_MS === 5000`; tries `false, false, true` give `true` after 3 calls and 2 sleeps of 5000; all `false` gives `false` after exactly 3 calls | Spec (issue `:1191`), D-1156 | `mcp-server/tests/audit/network-proof.test.ts:78`, `:83`, `:93` | ✅ |
| AC-2 | unit | Add and transcript: each URL sampled on its own; blocked only at its second try lets the proof hold; working at all three tries counts the failure after 3 calls | Spec, D-1156 | `network-proof.test.ts:105`, `:115` | ✅ |
| AC-3 | unit | The same for cancel (`mediaBlocked` with cancel's wall) and compile (`captionsBlocked`) | Spec, D-1156 | `network-proof.test.ts:125`, `:136` | ✅ |
| AC-4 | check | The typecheck, the build, and `run-cli.test.ts`, `runner-fake-backend.test.ts` and `census-signature.test.ts` pass | Local Canon (`FORBIDDEN_IMPORTS_KEPT`) | row 2 `mar-np-green.txt`, `mar-np-green-types.txt`, `mar-np-green-build.txt`; gate `mcp-types`, `mcp-build`, `mcp-unit` | ✅ |
| AC-5 | unit (guard) | Authoritative mode, no fixtures, and no matching failing record each give `undefined`; another signature is not probed; the probed keys equal the row-0 rule's; a URL blocked at its first try is called once with no sleep; passes at Red | Local Canon (`run.ts:547-577`), D-1160 | `network-proof.test.ts:145`, `:151`, `:158`, `:165`, `:179`, `:191` | ✅ |
| AC-6 | check | `mcp-audit.md` gains exactly the `WORKFLOW_NOTE` line after `:20`, nested, CRLF kept; `docs.test.ts` passes | Spec (issue `:1191`) | row 2 `mar-np-green-shape.txt`, `mar-np-green.txt` | ✅ |
| AC-7 | unit | The registered description is under 4,096 characters, line 1 is the lead, and it holds the zoom sentence | Human-approved (D-1134 A) | `mcp-server/tests/capture-description.test.ts:45` | ✅ |
| AC-8 | unit | Lines 2 to 5 start with the four markers in order and no other line does; lines 6 to 14 start with the nine actions in `ACTION_INDEX` order | Human-approved (D-1134 A), D-1157 | `capture-description.test.ts:53` | ✅ |
| AC-9 | unit | `DESC_TRACE` on lines 6 to 14 against the registered `_meta.action_descriptions` | D-1157 | `capture-description.test.ts:66` | ✅ |
| AC-10 | unit (guard), check | The other seven descriptions keep their row-0 SHA-256; capture's `_meta.action_descriptions` equals `captureDescriptions`; `desc-check.mjs` passes on `dist/` | Human-approved (D-1134 A), `DESC_PIN` | `capture-description.test.ts:83`, `:96`; row 4 `mar-desc-check.txt`; gate `desc-check` | ✅ |
| AC-11 | eval | `eval-rerun.py check` passes all three runs | Human-approved (D-1134 A), D-1158 | row 5 `mar-eval-check.txt` | ✅ |
| AC-12 | check | Row 7's authoritative run exits 0 and its summary passes `baseline-diff.py summary` | BASELINE_UPDATE_RULE, `AUDIT_RUN` | row 7 `mar-r7-audit.txt`, `mar-r7-summary-check.txt` | ✅ |
| AC-13 | check | The written baseline passes `baseline-diff.py baseline` against the row-0 copy; the baseline and report pass `check_home_path.py` | Human-approved (D-1159 A), BASELINE_UPDATE_RULE | row 7 `mar-r7-baseline-check.txt`, `mar-r7-home.txt`; gate `baseline-diff`, `home-path` | ✅ |
| AC-14 | Red then Green | The four coverage tests fail by assertion at row 6 (`Tests  4 failed`) and the file passes after row 7 | Local Canon (D-499, `coverage.test.ts:15-22`) | `mcp-server/tests/audit/coverage.test.ts:102`, `:153`, `:294`, `:324`; rows 6 and 7 | ✅ |
| AC-15 | check | The three issues `resolved` with `verification` and `resolution_path`, `meu_links` kept; the baseline issue's `blast_radius`, `verification.result` and `resolution_path` name all five keys; no D-1161 or D-1162 record, so the row added no issue; render check passes; grouping row 92 as planned | Local Canon (`tools/issue_triage*`), D-1161, D-1162 | row 8 `mar-issue-resolve.txt`, `mar-row8-check-d1164.txt` (D-1164); gate `issues-render-check` | ✅. D-1163's tracking issue was added after the row's check, outside AC-15's D-1161 and D-1162 clauses (Departures) |
| Coverage baseline tests (cross-ref) | Red then Green | `coverage.test.ts:102` and `:153`: the committed baseline against the action set less `BASELINE_PENDING`. Text unchanged; failed at row 6 and pass after row 7 | Local Canon (§Test pins) | rows 6 and 7; gate `mcp-unit` | ✅ |
| Coverage sheet and export tests (cross-ref) | Red then Green | `coverage.test.ts:294` and `:324`: retitled and re-asserted as named in §Test pins (Changed Files) | Local Canon (§Test pins, D-499) | rows 6 and 7; gate `mcp-unit` | ✅ |
| Pending fixture (cross-ref) | guard | `coverage.test.ts:160`: `pendingProblems(["avkit_capture.crop"], baselineKeys, ACTION_SET)` still reports `avkit_capture.crop is already in the baseline`; the rule under test is unchanged | Local Canon (§Test pins) | row 7 `mar-cov-green.txt` | ✅ |
| Forbidden imports (cross-ref) | guard | `mcp-server/tests/audit/run-cli.test.ts:91-103`: unchanged; it now scans the new `network-proof.ts` and passes | Local Canon (§Test pins; `FORBIDDEN_IMPORTS_KEPT`) | rows 1 and 2 (`mar-np-red-runner.txt`, `mar-np-green.txt`); gate `mcp-unit` | ✅ |
| Runner tests (cross-ref) | guard | `mcp-server/tests/audit/runner-fake-backend.test.ts`, `census-signature.test.ts`, `classify.test.ts` and `transcript-oracle.test.ts`: unchanged; pass at row 1 on the moved block and in the full run | Local Canon (§Test pins) | row 1 `mar-np-red-runner.txt`; row 2; gate `mcp-tests` | ✅ |
| Workflow docs test (cross-ref) | guard | `mcp-server/tests/audit/docs.test.ts`: unchanged; passes with the note | Local Canon (§Test pins) | row 2 `mar-np-green.txt`; gate `mcp-unit` | ✅ |
| Per-action texts (cross-ref) | guard | `mcp-server/tests/m7-resource.test.ts` and `mcp-server/tests/capture.test.ts`: byte-identical files; the 75 per-action texts, their markers and `_meta` pass | Local Canon (§Test pins; `DESC_PIN`) | row 4 `mar-desc-green.txt`; gate `mcp-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1 | `AssertionError: expected 1 to be 3 // Object.is equality` (`mar-np-red.txt`, `Tests  7 failed \| 6 passed (13)`) | Row 2: `Tests  41 passed (41)` (`mar-np-green.txt`) | `mcp-server/tests/audit/network-proof.test.ts:78`, `:83`, `:93` |
| AC-2 | `expected 1 to be 2` and `expected 1 to be 3` (`mar-np-red.txt`) | Row 2: `Tests  41 passed (41)` (`mar-np-green.txt`) | `network-proof.test.ts:105`, `:115` |
| AC-3 | `expected 1 to be 2` and `expected 1 to be 3` (`mar-np-red.txt`) | Row 2: `Tests  41 passed (41)` (`mar-np-green.txt`) | `network-proof.test.ts:125`, `:136` |
| AC-7 | `AssertionError: expected 'Workflow: capture or list ...' to be 'Call image to view a frame or sheet. ...'` (`mar-desc-red.txt`, `Tests  3 failed \| 2 passed (5)`) | Row 4: `Tests  73 passed (73)` (`mar-desc-green.txt`) | `mcp-server/tests/capture-description.test.ts:45` |
| AC-8 | `expected [ Array(1) ] to have a length of 14 but got 1` (`mar-desc-red.txt`) | Row 4: `Tests  73 passed (73)` (`mar-desc-green.txt`) | `capture-description.test.ts:53` |
| AC-9 | `expected [] to have a length of 9 but got +0` (`mar-desc-red.txt`) | Row 4: `Tests  73 passed (73)` (`mar-desc-green.txt`) | `capture-description.test.ts:66` |
| AC-14 | `AssertionError: expected { missing: [ ...(5) ], extra: [] } to deeply equal { missing: [], extra: [] }` (two tests) and `expected [ 'avkit_settings.get', ...(69) ] to include 'avkit_capture.sheet'` and `'avkit_capture.export'` (`mar-cov-red.txt`, `Tests  4 failed \| 14 passed (18)`) | Row 7: `Tests  18 passed (18)` (`mar-cov-green.txt`) | `mcp-server/tests/audit/coverage.test.ts:102`, `:153`, `:294`, `:324` |

- **Not in FAIL_TO_PASS:**
  - AC-5 and AC-10 passed at Red and are guards.
  - AC-4, AC-6, AC-12, AC-13 and AC-15 are checks.
  - AC-11 is the eval.
- **Each Red's receipt passed `red-check.py`.** It refuses exit 0, setup failures and non-assertion diagnostics:
  - `mar-np-red-check.txt`: `3 required test(s), 0 problem(s)`;
  - `mar-desc-red-check.txt`: `3 required test(s), 0 problem(s)`;
  - `mar-cov-red-check.txt`: `4 required test(s), 0 problem(s)`.
- **The test files are unchanged from Red to Green.** Each Green row checked the hash its Red row recorded (`mar-np-green-shape.txt`, `mar-desc-green-shape.txt`, `mar-r7-shape.txt`).

The four coverage tests' titles carry ids from earlier sessions' AC families: AC-68.5 (`coverage.test.ts:102`), AC-130.28 (`:153`), AC-135.19 (`:294`) and AC-136.18 (`:324`). The plan's text also quotes AC-68.2, the title of `run-cli.test.ts:91-103`, and D-1163 quotes AC-136.19, Session 64's eval AC. These ids belong to earlier sessions' families, not to this session's AC-1 to AC-15. They are named here once, mapped to file and line, so that the handoff carries every id the plan text holds (the closeout validator's coverage check). This handoff claims nothing for them beyond the rows above (Session 83 RULE-1).

#### Per-row evidence

**Row 0, baseline** (`mar-baseline.txt`)
- `baseline: all steps exit 0`; `anchor lines moved: none`; `ac10: 7 of 7 match the plan's table`.
- The register states:
  - `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` is at `:1191`, `open`;
  - `YOUTUBE-CAPTIONS-IP-BLOCK` is `resolved`.
- Capture's row-0 description is 145 characters.
- **Moved citations, fixed here (Session 51 RULE-3).** Both issues moved down one line in the register between plan time and row 0. They have moved again since, through row 8's resolve and D-1163's add.

  | Issue | Plan cites | Row 0 | Now |
  |---|---|---|---|
  | `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` | `:5126` | `:5127` (`line 5127 (moved from plan-time :5126)`) | `:5130` |
  | `MCP-AUDIT-BASELINE-PENDING-CROP` | `:5021` | `:5022` (`line 5022 (moved from plan-time :5021)`) | `:5024` |

**Row 0, the start condition** (grouping §5)
- `mar-caption-probe.txt`: `youtube-transcript-api 1.2.4`, `jNQXAC9IVRw OK 6 snippets`.
- `mar-adapter-probe.txt`: `VSU9VjZFoLI TranscriptResult language en chars 9648`.
- Neither printed `FAIL`.
- `mar-since.txt`: the commits from `ecfa3f3` to `HEAD` are `cba97fe` and `174bafa`. Neither touches an audit path.

**Row 0, the base MCP run** (`mar-base-mcp.txt`): `Test Files  36 passed (36)`, `Tests  535 passed (535)`.

**Row 1, Red**
- `mar-np-red.txt`: `Tests  7 failed | 6 passed (13)`. The failures are AC-1, AC-2 and AC-3 by assertion; AC-5's six tests passed.
- The runner tests on the moved block (`mar-np-red-runner.txt`): `Test Files  5 passed (5)`, `Tests  62 passed (62)`. The five files are run-cli, runner-fake-backend, census-signature, classify and transcript-oracle.
- `mar-np-red-shape.txt`: `vitest 7 failed, 6 passed: True AC-5 passed: True one sample: True probes moved: True run.ts CRLF: True`.

**Row 2, Green**
- `mar-np-green.txt`: `Test Files  5 passed (5)`, `Tests  41 passed (41)`. The five files are network-proof, docs, run-cli, runner-fake-backend and census-signature.
- The typecheck and the build exit 0.
- `mar-np-green-shape.txt`: `three samples: True mcp-audit.md one line added after 20: True note as planned: True CRLF: True`.

**Row 3, Red**
- `mar-desc-red.txt`: `Tests  3 failed | 2 passed (5)`. The failures are AC-7 to AC-9; AC-10's two guards passed.

**Row 4, Green**
- `mar-desc-green.txt`: `Test Files  3 passed (3)`, `Tests  73 passed (73)`. The three files are capture-description, capture and m7-resource.
- `mar-desc-check.txt`: `avkit_capture description: 3981 chars (limit 4096), equals expected: true`, `desc-check: ok`.
- `mar-desc-green-shape.txt`: `registry lines changed: [17, 172] registry as planned: True export present: True 05 paragraph as planned: True`.

**Row 5, eval** (D-1158, D-1186)
- `mar-eval-prep.txt`: `row5-prep: all steps exit 0`.
- The raw describe receipt (`mar-eval-describe-proof.txt`):
  - no cp437 mojibake;
  - valid UTF-8;
  - the description equals `capture-description.expected.txt` byte for byte, `3989 vs 3989 bytes`;
  - real arrows present: 9;
  - `describe-proof: ok`.
- The prompts: `prompts-proof: ok` (`mar-eval-prompts-proof.txt`).
  - The guard refused the cp437-decoded attempt-1 receipt with exit 2 and wrote no prompt (`mar-eval-prompts-guard-negative.txt`).
  - `eval-rerun selftest: ok` (`mar-eval-rerun-guard.txt`).
  - Each new prompt equals Session 64's prompt text on the clean surface (`mar-eval-prompt-compare.txt`: equal True for 24794, 24550 and 24519 characters).
- `mar-eval-check.txt`:

  | Run | What the run did | Result |
  |---|---|---|
  | t1 | 2 frames or sheet calls and 1 image call; slide `Velvet Margins 38` | `run s92-real-t1: pass` |
  | t2 | 2 sheet calls (needs 2); arrival `3954` | `run s92-real-t2: pass` |
  | t3 | 1 jpeg export of 428396 bytes, 1568x882, in the run's inbox | `run s92-real-t3: pass` |

  The receipt ends `eval-rerun check: ok`. The three reports are `mar-eval-real-t1-report.txt` to `-t3-report.txt`, each the subagent's final message, unedited.
- **The spend** (`mar-eval-spend.txt`): `eval spend: 860003 tokens in all, three runs, no rerun`. The plan estimated 0.5 to 2 million. All three subagents ran on `claude-haiku-5-5`.

  | Run | Assistant messages | Tokens |
  |---|---|---|
  | t1 | 7 | 318863 |
  | t2 | 9 | 416843 |
  | t3 | 3 | 124297 |

  Each count is input, cache creation, cache read and output, summed. How it was counted is under Departures.

**Row 6, Red**
- `mar-cov-red.txt`: `Tests  4 failed | 14 passed (18)`.
- `mar-cov-red-shape.txt`: `outside the named edits: [] BASELINE_PENDING empty: True baseline unchanged: True`.

**Row 7, audit**
- Setup: `mar-r7-ci.txt` reads `added 136 packages`, `mar-r7-sync.txt` reads `Checked 123 packages`, and the build exits 0.
- The run (`mar-r7-audit.txt`): `mcp-audit authoritative: 104/104 pass, 0 discovery finding(s), cleanup ok, exit 0`.
- The summary:
  - commit `cba97fe9795b8a76532c5c6fa9da37ffad10e206`, mode `authoritative`;
  - cleanup `ok` with `residuals: []`, `backend_exited: true`, `root_removed: true`;
  - discovery `pass`, 8 tools, 75 actions, with no findings and no removed or ghost key;
  - deltas: `UNCHANGED` 70 and `NEW` 5, the five keys;
  - counts: pass 104, fail 0, total 104.
- The baseline written:
  - schema `mcp-audit-baseline.v1`;
  - `recorded_commit` `cba97fe`, `recorded_at` `2026-11-18T14:12:39.266Z`;
  - `findings: []`, 75 entries.
- The checks:
  - `baseline-diff summary: ok` (`mar-r7-summary-check.txt`);
  - `baseline-diff baseline: ok` (`mar-r7-baseline-check.txt`);
  - `check_home_path: ok files=2630` (`mar-r7-home.txt`);
  - `Tests  18 passed (18)` (`mar-cov-green.txt`);
  - `eol-check: 19 scope path(s), 0 problem(s)` (`mar-r7-eol.txt`);
  - `mar-r7-shape.txt`: the coverage test is unchanged since Red, and the baseline and report are LF.
- D-1161 did not fire: there is no `mar-d1161.txt`.

**Row 8, records**
- `mar-issue-resolve.txt`:
  - `decision logs read: 104 of 104`;
  - register sha256 before `7193d377…`, after `2cd757a2…`, `CRLF=0 LF=5723`;
  - `parsed fields changed: 16`;
  - `issue-resolve: 0 problem(s)`.
- The render: `Rendered known-issues.md: 39 lines`, then `OK: known-issues.md is up-to-date`.
- The row's check, as written (`mar-row8-check.txt`), fails on `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` and is kept. Its D-1164 rerun (`mar-row8-check-d1164.txt`) exits 0 with every clause `True`:
  - `grouping lines changed: [164]`;
  - the three issues resolved with `meu_links` kept;
  - the baseline issue names the five keys;
  - `issues added: []`.
- Then D-1163 (`mar-issue-add-d1163.txt`): `OK: Added issue 'EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE' to known-issues.yaml`, `Rendered known-issues.md: 40 lines`, `OK: known-issues.md is up-to-date`, `d1163-issue: ok`.
- D-1162 did not fire: there is no `mar-d1162.txt`.

**H1 rows**
- H1-1 (`task-unchecked.txt`): `unchecked implementation rows: []`.
- H1-5 (`source-read-h1-5.txt`): `source-read: ok`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row0.ps1 (task.md row 0's Validation cell: baseline.ps1 records baseline.sha, the dirty list and hashes, the scope and skip hashes and the line-ending baseline, re-reads the anchors and the register states, runs caption_probe.py and adapter_probe.py, the MCP build and desc-check.mjs --record, the base typecheck and full MCP Vitest run, and the plan-local selftests); receipts mar-baseline.txt, mar-caption-probe.txt, mar-adapter-probe.txt, mar-desc-record.json, mar-base-mcp-types.txt, mar-base-mcp.txt, mar-since.txt", "scope": "Row 0: the baseline at cba97fe, the start condition (grouping §5) and the plan-local checkers", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD cba97fe (baseline.sha) plus row 0", "output": "mar-baseline.txt: baseline: all steps exit 0; anchor lines moved: none; issue MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL line 5127 (moved from plan-time :5126) status open; issue MCP-AUDIT-BASELINE-PENDING-CROP line 5022 (moved from plan-time :5021) status open; ac10: 7 of 7 match the plan's table. mar-caption-probe.txt: youtube-transcript-api 1.2.4; jNQXAC9IVRw OK 6 snippets. mar-adapter-probe.txt: VSU9VjZFoLI TranscriptResult language en chars 9648. mar-since.txt: ecfa3f3..HEAD is cba97fe and 174bafa, and neither touches an audit path. mar-base-mcp.txt: Test Files  36 passed (36); Tests  535 passed (535)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-1-red-census", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row1.ps1 (task.md row 1's Validation cell: network-proof.ts with NETWORK_PROOF_SAMPLES = 1 and run.ts wired by tmp/edit-run-ts.py, then npx vitest run tests/audit/network-proof.test.ts, red-check.py --require AC-1 --require AC-2 --require AC-3, the runner tests, the typecheck and the shape check); receipts mar-np-red.txt, mar-np-red-check.txt, mar-np-red-runner.txt, mar-np-red-types.txt, mar-np-red-shape.txt, mar-np-red-hashes.json", "scope": "AC-1 to AC-3 Red at one sample; AC-5 guards pass at Red; the runner tests pass on the moved block", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD cba97fe (baseline.sha) plus rows 0 and 1", "output": "mar-np-red.txt: AssertionError: expected 1 to be 3 // Object.is equality; expected 1 to be 2; Tests  7 failed | 6 passed (13). mar-np-red-check.txt: red-check: 1 receipt(s), 3 required test(s), 0 problem(s). mar-np-red-runner.txt: Test Files  5 passed (5); Tests  62 passed (62). mar-np-red-shape.txt: vitest 7 failed, 6 passed: True AC-5 passed: True one sample: True probes moved: True run.ts CRLF: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-2-green-census", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row2.ps1 (task.md row 2's Validation cell: NETWORK_PROOF_SAMPLES = 3 and the mcp-audit.md note by tmp/edit-row2.py, then npx vitest run tests/audit/network-proof.test.ts tests/audit/docs.test.ts tests/audit/run-cli.test.ts tests/audit/runner-fake-backend.test.ts tests/audit/census-signature.test.ts, the typecheck, the build, eol-check.py and the shape check); receipts mar-np-green.txt, mar-np-green-types.txt, mar-np-green-build.txt, mar-np-green-eol.txt, mar-np-green-shape.txt", "scope": "AC-1 to AC-3 Green, AC-4, AC-5 and AC-6: NETWORK_PROOF_SAMPLE, PROBES_SEAM, NETWORK_PROOF_GATHER, FORBIDDEN_IMPORTS_KEPT, WORKFLOW_NOTE", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD cba97fe (baseline.sha) plus rows 0 to 2", "output": "mar-np-green.txt: Test Files  5 passed (5); Tests  41 passed (41). The typecheck and the build exit 0. mar-np-green-shape.txt: test unchanged since Red; three samples: True mcp-audit.md one line added after 20: True note as planned: True CRLF: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-3-red-desc", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row3.ps1 (task.md row 3's Validation cell: npx vitest run tests/capture-description.test.ts, red-check.py --require AC-7 --require AC-8 --require AC-9, the shape check); receipts mar-desc-red.txt, mar-desc-red-check.txt, mar-desc-red-shape.txt, mar-desc-red-hashes.json", "scope": "AC-7 to AC-9 Red on the 145-character description; AC-10 guards pass at Red", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD cba97fe (baseline.sha) plus rows 0 to 3", "output": "mar-desc-red.txt: AC-7 AssertionError: expected 'Workflow: capture or list ...' to be 'Call image to view a frame or sheet. ...'; AC-8 expected [ Array(1) ] to have a length of 14 but got 1; AC-9 expected [] to have a length of 9 but got +0; Tests  3 failed | 2 passed (5). mar-desc-red-check.txt: red-check: 1 receipt(s), 3 required test(s), 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-4-green-desc", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row4.ps1 (task.md row 4's Validation cell: CAPTURE_TOOL_DESCRIPTION in capture.ts by tmp/edit-row4-capture.py, registry.ts :17 and :172 and the 05-mcp-server.md paragraph by tmp/edit-row4-rest.py, then npx vitest run tests/capture-description.test.ts tests/capture.test.ts tests/m7-resource.test.ts, the typecheck, the build, desc-check.mjs --baseline mar-desc-record.json --expected capture-description.expected.txt, eol-check.py and the shape check); receipts mar-desc-green.txt, mar-desc-green-types.txt, mar-desc-green-build.txt, mar-desc-check.txt, mar-desc-green-eol.txt, mar-desc-green-shape.txt", "scope": "AC-7 to AC-10 Green: CAPTURE_TOOL_DESCRIPTION, DESC_SHAPE, DESC_TRACE, DESC_PIN (D-1134 A, D-1157)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD cba97fe (baseline.sha) plus rows 0 to 4", "output": "mar-desc-green.txt: Test Files  3 passed (3); Tests  73 passed (73). mar-desc-check.txt: avkit_capture description: 3981 chars (limit 4096), equals expected: true; desc-check: ok. mar-desc-green-shape.txt: registry lines changed: [17, 172] registry as planned: True export present: True 05 paragraph as planned: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-5-eval", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row5-prep.ps1 (task.md row 5's Validation cell up to the subagents: the build, Session 64's eval-harness.ts describe and the three seeds), uv run python C:/Temp/av-kit/mcp-audit-refresh/tmp/describe-raw.py and tmp/prompts-raw.py (D-1186: the describe and eval-rerun.py prompts re-captured as raw bytes, with the guard's negative proof), three fresh general-purpose subagents with model haiku run by the coordinator, then pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row5.ps1 (eval-rerun.py check); receipts mar-eval-prep.txt, mar-eval-build.txt, mar-eval-describe.txt, mar-eval-describe-proof.txt, mar-eval-prompts.txt, mar-eval-prompts-proof.txt, mar-eval-prompts-guard-negative.txt, mar-eval-rerun-guard.txt, mar-eval-d1186-roundtrip.txt, mar-eval-prompt-compare.txt, mar-eval-real-t1-report.txt to -t3-report.txt, mar-eval-check.txt, mar-eval-spend.txt", "scope": "AC-11: the three Session 64 tasks on the new real surface (EVAL_RERUN, D-1158)", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD cba97fe (baseline.sha) plus rows 0 to 5", "output": "mar-eval-prep.txt: row5-prep: all steps exit 0. mar-eval-describe-proof.txt: no cp437 mojibake; description equals capture-description.expected.txt byte for byte: 3989 vs 3989 bytes; describe-proof: ok. mar-eval-prompts-proof.txt: prompts-proof: ok. mar-eval-prompts-guard-negative.txt: the cp437-decoded attempt-1 receipt refused, exit 2. mar-eval-rerun-guard.txt: eval-rerun selftest: ok. mar-eval-check.txt: t1 2 frames or sheet calls and 1 image call, slide 'Velvet Margins 38'; run s92-real-t1: pass; t2 2 sheet calls, arrival 3954; run s92-real-t2: pass; t3 1 jpeg export of 428396 bytes, 1568x882; run s92-real-t3: pass; eval-rerun check: ok. mar-eval-spend.txt: eval spend: 860003 tokens in all, three runs, no rerun."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-6-red-coverage", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row6.ps1 (task.md row 6's Validation cell: the four coverage.test.ts edits by tmp/edit-row6.py, npx vitest run tests/audit/coverage.test.ts, red-check.py --require for the four tests, the shape check); receipts mar-cov-red.txt, mar-cov-red-check.txt, mar-cov-red-shape.txt, mar-cov-red-hashes.json", "scope": "AC-14 Red: the four coverage tests fail against the row-0 baseline", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD cba97fe (baseline.sha) plus rows 0 to 6", "output": "mar-cov-red.txt: AssertionError: expected { missing: [ ...(5) ], extra: [] } to deeply equal { missing: [], extra: [] } (two tests); expected [ 'avkit_settings.get', ...(69) ] to include 'avkit_capture.sheet' and 'avkit_capture.export'; Tests  4 failed | 14 passed (18). mar-cov-red-check.txt: red-check: 1 receipt(s), 4 required test(s), 0 problem(s). mar-cov-red-shape.txt: outside the named edits: [] BASELINE_PENDING empty: True baseline unchanged: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-7-audit", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row7.ps1 (task.md row 7's Validation cell, after the host-load wait: npm --prefix mcp-server ci, uv sync --frozen --all-packages, the build, npm --prefix mcp-server run audit -- --mode authoritative --baseline <abs baseline> --out C:/Temp/av-kit/mcp-audit-refresh/audit-r7 --agent claude-code-session-92 --update-baseline --report <abs report>, baseline-diff.py summary and baseline, check_home_path.py, npx vitest run tests/audit/coverage.test.ts, eol-check.py and the shape check); receipts mar-r7-host.txt, mar-r7-ci.txt, mar-r7-sync.txt, mar-r7-build.txt, mar-r7-audit.txt, mar-r7-summary-check.txt, mar-r7-baseline-check.txt, mar-r7-home.txt, mar-cov-green.txt, mar-r7-eol.txt, mar-r7-shape.txt", "scope": "AC-12, AC-13 and AC-14 Green: AUDIT_RUN, AUDIT_TMP, BASELINE_RECORD (D-1159 A), PENDING_EMPTIED", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD cba97fe (baseline.sha) plus rows 0 to 7", "output": "mar-r7-ci.txt: added 136 packages. mar-r7-sync.txt: Checked 123 packages. The build exits 0. mar-r7-audit.txt: mcp-audit authoritative: 104/104 pass, 0 discovery finding(s), cleanup ok, exit 0; the summary: commit cba97fe9795b8a76532c5c6fa9da37ffad10e206, mode authoritative, cleanup ok with residuals [], backend_exited true, root_removed true; discovery pass, 8 tools, 75 actions, findings [], removed [], ghost []; deltas UNCHANGED 70 and NEW 5 (avkit_convert.probe, avkit_capture.crop, avkit_capture.frames, avkit_capture.sheet, avkit_capture.export); counts pass 104, fail 0, total 104. The baseline written: schema mcp-audit-baseline.v1, recorded_commit cba97fe, recorded_at 2026-11-18T14:12:39.266Z, findings [], 75 entries. mar-r7-summary-check.txt: baseline-diff summary: ok. mar-r7-baseline-check.txt: baseline-diff baseline: ok. mar-r7-home.txt: check_home_path: ok files=2630. mar-cov-green.txt: Tests  18 passed (18). mar-r7-eol.txt: eol-check: 19 scope path(s), 0 problem(s). mar-r7-shape.txt: coverage test unchanged since Red: True; baseline and report LF: True."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-8-records", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-row8.ps1 (task.md row 8's Validation cell: issue-resolve.py for the three issues bound to row 0's register hash, issue_triage.py render and render --check, the grouping row 92 edit by tmp/edit-row8-grouping.py, the row's final check), then uv run python C:/Temp/av-kit/mcp-audit-refresh/tmp/row8-check-fixed.py (D-1164: the row's own final check with its block slice cut at the next issue) and tmp/add-d1163-issue.py (D-1163: issue_triage.py add, render, render --check); receipts mar-issue-resolve.txt, mar-issues-render.txt, mar-issues-render-check.txt, mar-row8-check.txt (fails; kept), mar-row8-check-d1164.txt, mar-issue-add-d1163.txt", "scope": "AC-15: the three issues resolved, grouping row 92; D-1163's tracking issue", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD cba97fe (baseline.sha) plus rows 0 to 8", "output": "mar-issue-resolve.txt: decision logs read: 104 of 104; parsed fields changed: 16; issue-resolve: 0 problem(s). mar-issues-render.txt: Rendered known-issues.md: 39 lines; render --check: OK: known-issues.md is up-to-date. mar-row8-check.txt: MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL False (the block-slice defect, D-1164). mar-row8-check-d1164.txt: grouping lines changed: [164] row 92 as planned: True D-1161: False D-1162: False; the three issues resolved with meu_links kept: True; the baseline issue names the five keys: True; issues added: []; exit 0. mar-issue-add-d1163.txt: OK: Added issue 'EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE' to known-issues.yaml; Rendered known-issues.md: 40 lines; OK: known-issues.md is up-to-date; register CR 0; d1163-issue: ok."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-h1-2-session-gate", "command": "pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-rowH1-2.ps1 (task.md row H1-2's Validation cell, after the host load read at or below 50 %: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-17-mcp-audit-refresh/session-gate.ps1 *> C:/Temp/av-kit/mcp-audit-refresh/mar-gate-h1.txt); step receipts mar-D6-<step>.txt", "scope": "H1-2: the PROFILE D6 session gate from identity-before to identity-after: mcp-types, task-contract, scope-paths, line-endings, home-path, five selftests, py-format, py-lint, desc-check-syntax, mcp-unit, desc-check, baseline-diff, host-load, mcp-build, the full MCP Vitest run, issues-render-check and state-render", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "cba97fe9795b8a76532c5c6fa9da37ffad10e206+9e874365b0204249e950d45c1038fb9da715cf054489ab3b420abc0e33d06e4a", "output": "mar-gate-h1.txt: every run step exit=0; skipped with reasons: py-tests, py-types, ui-types, ui-lint, ui-tests, ui-build, ui-electron and openapi (every packages/, tools/, ui/ and tests/ file keeps its baseline-skip-hashes.json hash, H1-4) and mcp-audit (run authoritatively at row 7 on this tree); tested_state before and after equal; session-gate: all steps exit 0. mar-D6-scope-paths.txt: changed paths: 59 outside scope: []; read-never-changed files: 19 mismatch: []; head moved (S4): False. mar-D6-line-endings.txt: eol-check: 19 scope path(s), 0 problem(s). mar-D6-home-path.txt: check_home_path: ok files=2631. mar-D6-mcp-unit.txt: Test Files  5 passed (5); Tests  53 passed (53). mar-D6-desc-check.txt: desc-check: ok. mar-D6-baseline-diff.txt: baseline-diff baseline: ok. mar-D6-host-load.txt: samples [22, 17, 19, 7, 26], mean=18.2; host-load: 18.2 %. mar-D6-mcp-tests.txt: Test Files  38 passed (38); Tests  553 passed (553). mar-D6-issues-render-check.txt: OK: known-issues.md is up-to-date. mar-D6-state-render.txt: Drift check passed. mar-D6-identity-after.txt: tested_state cba97fe9795b8a76532c5c6fa9da37ffad10e206+9e874365b0204249e950d45c1038fb9da715cf054489ab3b420abc0e33d06e4a."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "mar-h1-3-h1-4-closeout-checks", "command": "uv run python C:/Temp/av-kit/mcp-audit-refresh/tmp/edit-h13-focus.py (the Session 92 paragraph on top of .agent/context/current-focus.md, by bytes, CRLF kept); pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-rowH1-3.ps1 (rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/mcp-audit-refresh/mar-render-check.txt); pwsh -NoProfile -File C:/Temp/av-kit/mcp-audit-refresh/tmp/run-rowH1-4.ps1 (task.md row H1-4's skip-basis check *> C:/Temp/av-kit/mcp-audit-refresh/skip-basis-check.txt)", "scope": "H1-3 (current-focus and the state render) and H1-4 (the skip basis, S12)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the H1-2 state plus H1-3's current-focus paragraph (current-focus.md is outside identity.py's inputs)", "output": "edit-h13-focus.py: current-focus.md: Session 92 entry prepended, 218 lines, CRLF kept. mar-render-check.txt: Drift check passed - SSOT loaded (159 MEUs, 12 phases). skip-basis-check.txt: packages, tools, ui or tests changes since row 0: []."}
```

### Quality Gate Results

| Step | Result (receipt) |
|------|------------------|
| Gate | `session-gate: all steps exit 0` (`mar-gate-h1.txt`); every run step `exit=0` |
| Identity | `tested_state cba97fe9795b8a76532c5c6fa9da37ffad10e206+9e874365b0204249e950d45c1038fb9da715cf054489ab3b420abc0e33d06e4a`, equal before and after (`mar-D6-identity-before.txt`, `mar-D6-identity-after.txt`) |
| Scope | `changed paths: 59 outside scope: []`; `read-never-changed files: 19 mismatch: [] baseline-dirty hash mismatch: []`; coordinator-owned: 6 changed, restamp hash mismatch `[]`; `head moved (S4): False` (`mar-D6-scope-paths.txt`) |
| Line endings | `eol-check: 19 scope path(s), 0 problem(s)` (`mar-D6-line-endings.txt`) |
| Home path | `check_home_path: ok files=2631` (`mar-D6-home-path.txt`) |
| Task contract | `OK: 26 row(s); 2 exempt (view_file): H1-5, H2-1` (`mar-D6-task-contract.txt`) |
| Selftests | red-check `57 fixture(s), 0 wrong`; eol-check `24 case(s), 0 wrong`; desc-check, eval-rerun and baseline-diff `ok` |
| MCP unit, targeted | `Test Files  5 passed (5)`, `Tests  53 passed (53)` (`mar-D6-mcp-unit.txt`) |
| Description | `desc-check: ok` (`mar-D6-desc-check.txt`) |
| Baseline | `baseline-diff baseline: ok` (`mar-D6-baseline-diff.txt`) |
| Host load | samples `[22, 17, 19, 7, 26]`, `mean=18.2`, `host-load: 18.2 %` (`mar-D6-host-load.txt`) |
| MCP build | exit 0 (`mar-D6-mcp-build.txt`) |
| MCP Vitest, full | `Test Files  38 passed (38)`, `Tests  553 passed (553)` (`mar-D6-mcp-tests.txt`; row 0 had 535 in 36 files, and the two new files add 18) |
| Registers | `OK: known-issues.md is up-to-date` (`mar-D6-issues-render-check.txt`); the state render's drift check passed (`mar-D6-state-render.txt`) |
| Skipped | `py-tests`, `py-types`, `ui-types`, `ui-lint`, `ui-tests`, `ui-build`, `ui-electron`, `openapi`: every `packages/`, `tools/`, `ui/` and `tests/` file keeps its row-0 hash (H1-4); `mcp-audit`: run authoritatively at row 7 on this tree |
| H1-3 | `Drift check passed — SSOT loaded (159 MEUs, 12 phases)` after the current-focus paragraph (`mar-render-check.txt`) |
| H1-4 | `packages, tools, ui or tests changes since row 0: []` (`skip-basis-check.txt`) |

---

## Changed Files

Counts are added and removed lines against `HEAD` `cba97fe` (`git diff --numstat --ignore-cr-at-eol`). A new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step, `mar-D6-line-endings.txt`).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `mcp-server/scripts/audit/network-proof.ts` | new: `NETWORK_PROOF_SAMPLE`, `PROBES_SEAM`, `NETWORK_PROOF_GATHER` | 161 lines | LF |
| `mcp-server/scripts/audit/run.ts` | the census block becomes the `gatherNetworkProof` call; the three probes and the `NETWORK_STEP_URLS` import removed; one comment line | +4 / -86 | CRLF kept |
| `mcp-server/tests/audit/network-proof.test.ts` | new: AC-1 to AC-3, AC-5 | 198 lines | LF |
| `.agent/workflows/mcp-audit.md` | `WORKFLOW_NOTE` after `:20` | +1 / -0 | CRLF kept |
| `mcp-server/tests/capture-description.test.ts` | new: AC-7 to AC-10 | 103 lines | LF |
| `mcp-server/src/toolsets/capture.ts` | `CAPTURE_TOOL_DESCRIPTION` and the hoisted constants; `captureDescriptions` byte-identical | +64 / -18 | CRLF kept |
| `mcp-server/src/toolsets/registry.ts` | `:17` import, `:172` | +2 / -2 | CRLF kept |
| `docs/build-plan/05-mcp-server.md` | the paragraph after `:103` | +2 / -0 | CRLF kept |
| `mcp-server/tests/audit/coverage.test.ts` | the four §Test pins edits | +11 / -13 | CRLF kept |
| `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` | written by the audit (five entries, new `recorded_commit` and `recorded_at`) | +27 / -2 | CRLF to LF, by the tool |
| `.agent/context/MCP/mcp-tool-audit-report.md` | written by the audit | +48 / -37 | LF |
| `.agent/context/known-issues.yaml` | three issues resolved (`issue-resolve.py`); `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` added (`issue_triage.py add`, D-1163) | +24 / -13 | LF kept |
| `.agent/context/known-issues.md` | `issue_triage.py render` | +4 / -6 | LF |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | row 92 (`:164`): `executed (Session 92)` and the plan folder | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 92 paragraph (H1-3) | +3 / -0 | CRLF kept |
| `.agent/context/handoffs/2026-11-17-mcp-audit-refresh-handoff.md` | this handoff (H1-6) | new | LF |
| `.agent/context/handoffs/2026-11-17-mcp-audit-refresh-implementation-critical-review.md` | the H1-7 execution review, a byte copy of the reviewer's report | new | as written by the reviewer |
| `docs/execution/plans/2026-11-17-mcp-audit-refresh/` | the plan (execution notes; D-1163 and D-1164 added), task (row marks), the plan-local scripts (`baseline.ps1`, `identity.py`, `red-check.py`, `eol-check.py`, `issue-resolve.py`, `desc-check.mjs`, `eval-rerun.py` with the D-1186 guard, `baseline-diff.py`, `caption_probe.py`, `adapter_probe.py`, `host-load.ps1`), `capture-description.expected.txt`, the row-0 records and `session-gate.ps1` | new folder | LF |

**The four `coverage.test.ts` edits (§Test pins, named M-7 edits that D-499 designed):**

| Line now (row 0) | Old | New |
|------------------|-----|-----|
| `:23-24` (`:23-29`) | `const BASELINE_PENDING = [` with the five keys | `// Session 92 (mcp-audit-refresh): the authoritative update recorded all five; MCP-AUDIT-BASELINE-PENDING-CROP is resolved.` and `const BASELINE_PENDING: string[] = [];` |
| `:160` (`:165`) | `expect(pendingProblems(BASELINE_PENDING, [...baselineKeys, "avkit_capture.crop"], ACTION_SET)).toEqual([` | `expect(pendingProblems(["avkit_capture.crop"], baselineKeys, ACTION_SET)).toEqual([` |
| `:294-302` (`:299-304`) | title "... sheet parity and audit coverage: BASELINE_PENDING ends with the served sheet action"; the comment on export following sheet; `expect(BASELINE_PENDING.slice(-2)).toEqual(["avkit_capture.sheet", "avkit_capture.export"]);` | title "... sheet parity and audit coverage: the committed baseline holds the served sheet action"; ``const keys = parseBaseline(JSON.parse(readFileSync(COMMITTED_BASELINE, "utf8"))).entries.map((e) => `${e.tool}.${e.action}`);``, `expect(BASELINE_PENDING).toEqual([]);`, `expect(keys).toContain("avkit_capture.sheet");` |
| `:324-329` (`:328-332`) | title "... export parity and audit coverage: BASELINE_PENDING ends with the served export action"; `expect(BASELINE_PENDING[BASELINE_PENDING.length - 1]).toBe("avkit_capture.export");` | title "... export parity and audit coverage: the committed baseline holds the served export action"; the same three lines for `avkit_capture.export` |

The expected string at `:160` (`avkit_capture.crop is already in the baseline`) is unchanged, so the rule under test is the same. No other assertion in any file changed (M-7). `mar-cov-red-shape.txt` reads `outside the named edits: []`. `mcp-server/tests/capture.test.ts` and `mcp-server/tests/m7-resource.test.ts` are byte-identical to row 0. They are among the gate's `read-never-changed files: 19 mismatch: []` (`mar-D6-scope-paths.txt`). Line numbers are the current file's unless marked row 0. The plan's §Test pins gives them at `HEAD` `cba97fe`.

**Paths that are not this session's** (excluded from scope checks and from the commit paths):
- Six coordinator-owned paths changed after row 0 (D-1185, `mar-coordinator-owned.txt`). The coordinator commits them separately:
  - `.agent/model-registry.local.json`;
  - `.claude/agents/av-kit-builder.md`, `.claude/agents/av-kit-peer-reviewer.md` and `.claude/agents/av-kit-verifier.md`;
  - `.cursor/agents/av-kit-builder.md` and `.cursor/agents/av-kit-verifier.md`.
- Sessions 91, 93 and 94's plan folders and plan-review handoffs.

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

No findings: the round 1 review's Findings table is empty.

### Verdict

`approved` at round 1 of 6, with 0 findings and 0 blocking, intent achieved (`.agent/context/handoffs/2026-11-17-mcp-audit-refresh-implementation-critical-review.md`, a byte-for-byte copy of the reviewer's report, checked with `cmp`; ledger loop `mar-execution-2026-11-17-mcp-audit-refresh`, round 1 `verdict=approved agent='codex-independent-reviewer' blocking=0 intent_achieved=yes usage=20,487,519`, `loop may close: approved with no blocking findings.`).

- **The loop.** It began with the plan's goal anchor and AC list and no `--token-budget`. The OK line reads `mode=execution budget=6 tokens=off` (`mar-exec-begin.txt` in the dispatch folder). Dispatch `mar-exec-r1` ran with `-Kind execution` (timeout 2700 s); its console, `mar-exec-console-r1.txt` in the dispatch folder, ends with exit 0.
- **The state.** The reviewer's own `identity.py --state-only` returned the gate's tested_state `cba97fe9795b8a76532c5c6fa9da37ffad10e206+9e874365b0204249e950d45c1038fb9da715cf054489ab3b420abc0e33d06e4a` exactly, before and after its review (review frontmatter and §Scope, record `mar-review-r1-1`).
- **What it accepted.**
  - NETWORK_PROOF_SAMPLE, PROBES_SEAM, NETWORK_PROOF_GATHER and FORBIDDEN_IMPORTS_KEPT (§Q2): all eight three-answer sequences, an exception that propagates without a retry, and the three probe bodies unchanged from row 0.
  - CAPTURE_TOOL_DESCRIPTION, DESC_SHAPE, DESC_TRACE and DESC_PIN (§Q3): every action map, input schema and the other seven descriptions unchanged on the built server.
  - EVAL_RERUN and the D-1186 encoding correction (§Q4): its surface probe rebuilt the served surface through the SDK's own validation and found it equal to the saved raw describe; the unchanged Session 64 checker passes all three runs.
  - AUDIT_RUN, AUDIT_TMP, BASELINE_RECORD and PENDING_EMPTIED under D-1159 A (§Q5): 70 entries unchanged and exactly five plain pass additions.
  - The gate, the registers and D-1164's check (§Q6), and the scope (§Q7): all 37 manifest hashes matched H1-6, all 19 read-never-changed files and all 686 skip hashes matched row 0.
- **What it did not rerun.** The audit, the eval agents, the build and the full MCP suite. It accepted their saved evidence against the matching identity and ran only targeted tests (`Tests 36 passed (36)`) and read-only probes (§Q1).
- **Residuals it names.** The approved extra container-probe latency, and one Haiku run per task.
- **H1-7a** (`review-state-check.txt`, `review-state.json`): `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`.
- **H1-7b** (`exec-review.txt`): `OK: approved at round 1 of 6, 0 open blocking findings`.
- **After the review**, only this handoff changed, to fill this report, so its sha256 differs from the one the review's manifest check read. No other session path changed.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Session 64's eval describe capture (`eval-run.md` step 3, task row E-1) decodes UTF-8 through cp437; Session 64's own eval ran on that surface | registered | `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` (open) | D-1163, D-1186; Session 64's files are another session's evidence and are unchanged |
| Descriptions of the other seven tools | out-of-scope | — | D-1134 A: they keep their descriptions until a miss is measured |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2-5) |

### Departures and their basis

- **The plan and task hashes.**
  - The coordinator applied the plan review's non-blocking note before execution, as execution notes at `implementation-plan.md:37`, `:320` and `:425` and at `task.md:36`. The eval harness starts the isolated real backend, not a fake one (`eval-harness.ts:30,78-85,99-107`).
  - The plan's sha256 moved from the approved `e86ecbf8ba8a…` to `f45a4f1faec34377f42c0d5a4dc38e653871e532cc3d406936f74cfff52a1d52`, and task.md's from `ed299c128443…` to `ada3805da47f…` (`mar-exec-notes.txt`).
  - At H1-6, D-1163 and D-1164 were appended to the plan's decision YAML, 30 lines with no CR and no backslash. The plan's sha256 is now `cee18d4c6c19d2e42e7abd40ede63ee36c59202c19ebd1bd8db1c43bb962ebe9` (`mar-plan-decisions.txt`). The H2-2 reader's `decision_sources` reads D-1155 to D-1164 from it, both new ones at stage `execution`.
  - Since then, task.md has changed only by its row marks. The plan and task are outside `identity.py`'s inputs, so the state did not move.
- **D-1186 (the coordinator's ruling): the eval surface's mojibake.**
  - Row 5's first describe receipt and its three prompts held cp437 mojibake. They were captured the way Session 64's `eval-run.md` step 3 does it, through a PowerShell redirect of native output, which decodes the UTF-8 through the console code page and writes CRLF.
  - Before any subagent ran, the coordinator ruled D-1186:
    - re-capture the describe as raw bytes (`tmp/describe-raw.py`);
    - add a fail-closed guard to this plan's `eval-rerun.py prompts`, which refuses cp437 mojibake and requires the expected description verbatim;
    - rebuild the prompts from the raw receipt (`tmp/prompts-raw.py`).
  - `mar-eval-d1186-roundtrip.txt` proves the defect is only that decoding. The attempt-1 receipt, with CRLF made LF and undone through cp437, equals the raw receipt. Each attempt-1 prompt, undone the same way, equals its new prompt.
  - The attempt-1 files are kept under `-attempt1` names.
  - Session 64's own describe receipt (`s64-E1-describe.txt` in `RECEIPTS_DIR`) has the same mojibake arrows and no real one. So Session 64's three eval runs read a corrupted surface. That is recorded in `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` (D-1163), and Session 64's files are not changed.
- **D-1164: row 8's check.**
  - The row's final check cuts an issue's block at the first `- id: `, which also starts each `enrichment.decision_log` entry. It therefore never saw `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`'s `resolution_path`, which sits after enrichment, and it failed (`mar-row8-check.txt`, kept).
  - The row's own check was rerun with only that boundary moved to the next issue (`tmp/row8-check-fixed.py`) and passed (`mar-row8-check-d1164.txt`).
  - The register is unchanged by the rerun. The row cannot rerun as written, because `issue-resolve.py` is bound to row 0's register hash.
- **D-1163: the new issue was added after the row 8 check.**
  - The check's `issues added: []` was true when it ran. `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE` was added afterwards, through `issue_triage.py add`, render and render --check (`mar-issue-add-d1163.txt`).
  - AC-15's clause "with neither, no issue is added" concerns D-1161 and D-1162, which did not fire. This issue is D-1163's tracking row.
- **D-1185 (the coordinator's ruling): the six coordinator-owned paths.** They changed after row 0 and are foreign to this session, so they are excluded from scope and commit paths. The gate's scope step recorded them as `coordinator-owned: 6 changed` with no hash mismatch.
- **The sibling sessions.** The gate's scope step skipped 14 other sessions' plan files and three sibling plan-review handoffs, as foreign. One of the handoffs appeared after row 0. The step also printed a drift in Session 91's `e2e-pointer-flakes/implementation-plan.md` without failing on it: that file is another session's, and this session never wrote it.
- **The row-0 network probes.** Row 0 ran the triage's caption and adapter probes (`caption_probe.py`, `adapter_probe.py`) as the start condition. They read YouTube once each and upload nothing.
- **`run.ts` and `capture.ts` beyond the contract text.**
  - `run.ts` keeps one comment line at the call site, naming `network-proof.ts`. That line is counted in its `+4`.
  - `capture.ts` hoists the flatten, revert and annotate-newline sentences and the four `desc()` marker sentences into constants, which both `captureDescriptions` and `CAPTURE_TOOL_DESCRIPTION` read. `desc-check` proves `captureDescriptions` is byte-identical.
- **The desc-check order in the gate.** `desc-check` (a targeted step) runs on `dist/` before `mcp-build` (a fresh full step), so it read the `dist/` that rows 4 and 7 built from the same sources. The later `mcp-build` exited 0, and `mcp-tests` passed on it.
- **How the rows ran.**
  - Each row's Validation cell was extracted into a `.ps1` file (an environment header, then the cell) by `tmp/make-row-ps1.py` and run with `pwsh -NoProfile -File`.
  - The edits that rows name were made by byte-level Python scripts under the session's `tmp` folder, which keep each file's line endings.
  - The host-load wait (50 % or less) ran before each Red, each build, row 7 and H1-2.
- **The eval spend.** The coordinator did not report a token count, so `tmp/eval-spend.py` summed it read-only from the three subagents' own transcript usage records: one record per assistant message id, the last one kept. The receipt names their folder only as the home folder's.
- **Execution decisions** D-1163 and D-1164 are in the plan's decision YAML, each `resolution: autonomous`, `class: two-way` and `mandatory: []`. D-1155 to D-1162 are the plan's. D-1185 and D-1186 are the coordinator's rulings, recorded here in prose. So the Decision Log below is `None.`.

### Execution notes

- **D-1161 and D-1162 were not taken.** Row 7's run and both baseline checks passed, and all three eval runs passed. There is no `mar-d1161.txt` or `mar-d1162.txt`, so no AC is recorded as not met.
- **The decisions.**

  | Id | What was decided |
  |---|---|
  | D-1155 | No MEU. |
  | D-1156 | "Any sample blocked", which departs from the issue's literal "every sample", because extra samples under that rule make its symptom worse. |
  | D-1157 | The layout and `DESC_TRACE`. |
  | D-1158 | The eval as the acceptance check. |
  | D-1159 | Mat's ruling A on 2026-11-18: record all five keys. |
  | D-1160 | The probes seam. |
  | D-1163 | Register the cp437 issue. |
  | D-1164 | Rerun row 8's check with its block boundary fixed. |

- **Processes.** Each run stopped only the processes it launched, by recorded id and creation time. No process of another session, and not the IDE's avkit server, was stopped or called.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-18 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 to H1-5 |
| Reviewed | 2026-11-18 | codex-independent-reviewer | H1-7 execution review round 1: `approved`, 0 findings; the Codex Validation Report is filled from it |
