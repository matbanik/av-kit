---
date: "2026-11-15"
project: "2026-11-15-hdp-v2-protocol"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-hdp-v2-protocol/implementation-plan.md"
build_plan_section: "none (framework docs; no MEU, D-821)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-15-closeout-record-once-handoff.md"
---

# Handoff: 2026-11-15-hdp-v2-protocol-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. These are framework docs with no MEU (D-821), Session 85 of the HDP v2 and framework sync grouping (`.agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md`). It ports the protocol part (HD1) of `P:/agentic-framework` commit `a73d6df` ("feat(hdp): port the decision protocol and the expert pass"). Session 84 ported its closeout-validator part; Session 86 owns §5a, the expert-pass skill and the §6 hand-over rule.

- **`.agent/docs/human-decision-protocol.md`** (row 1): eight H2 headings, §1 to §7 plus §4a. §2 reads `.agent/context/current-focus.md` first and applies and cites a prior ruling; §3 is "Research", where a local measurement counts; §4 is the base §4 with one sentence changed; §4a lists M-1 to M-14, with `hdp` as the only mode (D-820) and five notes; §5 is Brief v2 (plain-words recommendation first, the other options compared with it, a do-nothing option, a Refs line; no "Default if unanswered" and no `SIGN 3 (a)`); §6 records each decision once, in the log of the stage that made it, and states the Session 84 validator's clauses, each bound in `validator-binding.json`; §7 "Basis" replaces "Anti-patterns" and "Research basis". 22,754 bytes, 306 lines, all CRLF.
- **`AGENTS.md:27`** (row 3): the decide-before-you-ask rule in place of the old pipeline sentence; 126 lines, 17,891 bytes; the rule-preservation postimage digest is repinned.
- **The four templates and their twins** (row 2): the v2 brief with the C line, the optional `mandatory:` field, the reflection's Decisions Log as a short link list, and the handoff Decision Log as one comment plus one yaml block. Each twin is byte-identical.
- **`model-delegation.md`** (row 4): the `Open decisions` bullet; line 5 keeps its bare LF.
- **Nine workflows** (row 5) and **five docs and two skills** (row 6): every stale phrase and every invalid protocol citation is gone from the live tree.

Not in scope: `tools/validate_closeout_artifacts.py` (`VALIDATOR`, unchanged at sha256 `94c7ac24ab354d7aad8235fa452cecf3b32ab809909127d57f7289342e8b99ed`), `P:/agentic-framework`, `P:/zorivest` and `P:/.agent`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | static | `PROTOCOL`'s H2 headings are exactly the eight in §The protocol rewrite, in order | Spec (`UPSTREAM`); Local Canon (D-841) | `hdp-check.py` C3 ok; selftest F01 refused | ✅ |
| AC-2 | static | The head keeps av-kit's scope and carries `PROTOCOL_HEAD_MARKERS`; §1 is present | Spec (`UPSTREAM`); Local Canon (D-845) | C3 ok; selftest F11 refused | ✅ |
| AC-3 | static | §2 has the `current-focus.md` row first, the apply-and-cite sentence, every base sweep row and both rg receipt commands | Spec (`UPSTREAM`); Local Canon (D-842) | C3 ok; selftest F08, F09 refused | ✅ |
| AC-4 | static | §3 is "Research", with the local-measurement sentence and av-kit's ladder and angles table | Spec (`UPSTREAM`); Local Canon (D-842) | C3 ok | ✅ |
| AC-5 | static | §4 equals `BASE`'s §4 except `S4_OLD` → `S4_NEW` | Spec (`UPSTREAM`) | C3 ok; selftest F02, F03 refused | ✅ |
| AC-6 | static | §4a: `hdp` only, M-1 to M-14 once each in order, each row carrying its own `M_ROWS` criterion phrases and its own av-kit source phrases; none of `S4A_FORBIDDEN`; "Five notes:" with five bullets, no `human-all` | Human-approved (D-843); Local Canon (D-820, D-845) | C3 ok; selftest F04, F05, F12, F35, F36 refused | ✅ |
| AC-7 | static | §5 has `S5_ORDERED` in order, with the C line; no `SIGN 3 (a)`, `gate-wait-then-exit` or `§5a` | Spec (`UPSTREAM`); Local Canon (D-840, D-845) | C3 ok; selftest F06, F07 refused | ✅ |
| AC-8 | static | §6 has `S6_MARKERS` and none of `S6_FORBIDDEN`; no hand-over paragraph | Spec (`UPSTREAM`); Local Canon (D-851) | C3 ok; selftest F10 refused | ✅ |
| AC-9 | static | §6 states `S6_VALIDATOR`'s clauses: each `ORACLE.TOPICS` topic is bound, with its fixed clause in §6 and every one of its fixed selectors passing in `EVIDENCE`, or dropped, with its clause absent, none of its evidence present and a reason | Local Canon (D-850, D-855) | C11 ok with `validator-binding.json` (25 topics, none dropped) and both `EVIDENCE` receipts; selftest F31 to F34, F38 to F41 refused | ✅ |
| AC-10 | static | §7 "Basis" carries `S7_MARKERS`; "Anti-patterns" and "Research basis" are gone from `PROTOCOL` | Spec (`UPSTREAM`) | C2, C3 ok; selftest F18 refused | ✅ |
| AC-11 | static | `AGENTS.md` holds `AGENTS_NEW` and not `AGENTS_OLD`; 126 lines; ≤ 20,000 bytes; the rule-map digest equals `AGENTS.md`'s; `test_framework_adoption.py` passes | Human-approved (D-844); Local Canon (D-846) | C4, C7 ok; `tests/tooling/test_framework_adoption.py` 91 passed (gate `adoption`) | ✅ |
| AC-12 | static | `model-delegation.md` holds `DELEGATION_NEW`; line 5 stays bare LF; every other line stays CRLF | Spec (`UPSTREAM`); Local Canon (D-847) | C4, C6 ok; selftest F20, F25, F25b refused | ✅ |
| AC-13 | static | The four templates hold `REQUIRED_TEXT` and none of `FORBIDDEN_TEXT`; each twin is byte-identical; the handoff Decision Log is one comment plus one yaml block; the template-mode task lint passes; `VALIDATOR --selftest` reports 0 failures | Spec (`UPSTREAM`); Local Canon (D-840, D-851) | C4, C5, C9 ok; template-mode task lint `OK: 19 row(s)` (gate `task-template`); `VALIDATOR --selftest` `231 arm(s), 0 failure(s)` (gate `closeout-selftest`); selftest F22, F23, F29 refused | ✅ |
| AC-14 | static | `create-plan.md` and `session-grouping.md` hold their `REQUIRED_TEXT` (including `CP_TEST_SEARCH` and `GROUPING_HEADER`) and not `**Recommendation:** {Option A}` | Spec (`UPSTREAM`) | C4 ok; selftest F21 refused | ✅ |
| AC-15 | static | Every protocol `§` citation in the live tree and `tools/` names §1 to §7 or §4a | Local Canon (D-841, D-852) | C1 ok; selftest F13 to F16 refused | ✅ |
| AC-16 | static | No `STALE_EVERYWHERE` phrase in the live tree; no `STALE_PROTOCOL_ONLY` phrase in `PROTOCOL` | Local Canon (D-852) | C2 ok; selftest F17 refused | ✅ |
| AC-17 | static | Each EDITED file keeps its row-0 work-tree line endings (C6); no uncensused numeric model name in an EDITED file (C8); the `issue-lifecycle-guide.md` boxes keep their line lengths (C10) | Local Canon (D-854; the CRLF rule) | C6, C8, C10 ok; selftest F24, F28, F30 refused | ✅ |
| AC-18 | static | Scope: `scope-check.py --check` passes. Every changed path is in EDITED, this plan folder or the closeout artifacts, or dirty at row 0 with its row-0 hash; `VALIDATOR`'s hash equals row 0's; HEAD equals `baseline.sha` | Local Canon (D-850; S4) | `scope-check.py --check` `scope-check: ok` (gate `scope-paths`); its selftest refuses each planted case | ✅ |
| AC-19 | static | `ORACLE --selftest`, `scope-check.py --selftest`, `identity.py --selftest` and `s84-landed.py --selftest` report 0 failures | Local Canon (D-848) | `hdp-check.py --selftest` 0 failures (46 ok lines), `scope-check.py --selftest` 0 failures, `s84-landed.py --selftest` 0 failures (all in the gate); `identity.py --selftest` 0 failures (row 0 and `identity-selftest-h16.txt`) | ✅ |

`AC-940` is not an av-kit AC. The plan cites Zorivest's `AC-940.4` (`implementation-plan.md:461`, `:515`, `:657`) as a precedent for the §4a adaptation, and the closeout validator's AC-id pattern reads it as a plan AC. It is listed here so that the coverage check sees it; there is nothing to deliver for it in av-kit.

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| `hdp-check.py` C1 (AC-15) | `C1 FAIL (1)` | `C1 ok` | `C:/Temp/av-kit/hdp85/hdp-red.txt`, `C:/Temp/av-kit/hdp85/hdp-green.txt` |
| `hdp-check.py` C2 (AC-10, AC-16) | `C2 FAIL (38)` | `C2 ok` | same |
| `hdp-check.py` C3 (AC-1 to AC-8, AC-10) | `C3 FAIL (63)` | `C3 ok` | same |
| `hdp-check.py` C4 (AC-11 to AC-14) | `C4 FAIL (29)`, e.g. `.agent/workflows/create-plan.md still holds '**Recommendation:** {Option A}'` | `C4 ok` | same |
| `hdp-check.py` C11 (AC-9) | `C11 FAIL (1)`: `not run: pass --binding validator-binding.json` | `C11 ok` with the binding | same |

Row 0's Red was `hdp-check: 132 failure(s)` with exit 1, as the row requires (`hdp-baseline.txt`: `baseline step hdp-red exit=1 (must be 1)`). C5 to C10 already held at the base and still hold: they are guards (twins, line endings, `AGENTS.md` size, model census, the handoff Decision Log shape, box widths). Green: row 7's full run `hdp-check: all checks pass` (`hdp-green.txt`) and the gate's `hdp-check` step.

`EVIDENCE` and `BINDING`:
- `C:/Temp/av-kit/hdp85/hdp-base-closeout-selftest.txt`: `RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms]`.
- `C:/Temp/av-kit/hdp85/hdp-base-s84-tests.txt`: `101 passed`.
- `validator-binding.json` (sha256 `c13ce8a08050dc1894118f988d46687b08e0ec3887c4ac428603f4cc9431c937`): 25 topics, each `{"topic"}`; **no topic is `dropped_by_s84`**, because Session 84 landed every clause (`s84-landed: Session 84 is closed`). The 25th topic, `dq-escapes`, was added in execution (D-856).

Receipts, all under `C:/Temp/av-kit/hdp85/`:
- `hdp-baseline.txt`, `hdp-base-py.txt`, `hdp-base-closeout-selftest.txt`, `hdp-base-s84-tests.txt`, `hdp-red.txt` (row 0);
- `hdp-row1.txt` (row 1); `hdp-row2.txt`, `hdp-row2-closeout-selftest.txt`, `hdp-template-lint.txt` (row 2); `hdp-row3.txt`, `hdp-adoption.txt` (row 3); `hdp-row4.txt` (row 4); `hdp-row5.txt` (row 5); `hdp-row6.txt` (row 6); `hdp-green.txt`, `hdp-selftest.txt`, `hdp-scope.txt` (row 7);
- the scope check before each edit row, `scope-pre-row1.txt` to `scope-pre-row6.txt`, and after the H1-3 edit, `scope-post-h13.txt`; all `scope-check: ok`;
- the re-baseline: `rebaseline.txt`, `rebase-diff-names.txt`, `scope-post-rebaseline.txt`, `s84-landed-post-rebaseline.txt`, and the old baseline files in `pre-rebaseline/`;
- Session 86's anchor probe, `ep-anchors-row7.txt` (`anchors: ok`; the row 1 probe `ep-anchors-row1.txt` reported the delegation bullet missing, which row 4 then added);
- `task-unchecked.txt` (H1-1); `hdp-gate-h1.txt` and `hdp-D6-<step>.txt` (H1-2); `hdp-render-check.txt` (H1-3); `openapi-check.txt` (H1-4); `identity-selftest-h16.txt` (AC-19, after the gate).

Each row ran its task.md Validation cell verbatim, written by `C:/Temp/av-kit/hdp85/rowcmd.py` into `C:/Temp/av-kit/hdp85/row-<id>.ps1` after the row environment (`Set-Location P:/av-kit`, `PYTHONIOENCODING=utf-8`, `RECEIPTS_DIR=C:/Temp/av-kit`) and run as `pwsh -NoProfile -File`. The edits were made by Python scripts in `C:/Temp/av-kit/hdp85/` (`r1-write-protocol.py`, `r2-templates.py`, `r3-agents.py`, `r5-workflows.py`, `r6-docs.py`, `h13-focus.py`): each asserts that the file is pure CRLF, replaces each old text exactly once in LF-normalised text, and writes CRLF back.

**Execution notes.** Each is a deviation from the plan or a row's command as written.

- **HEAD moved by Mat's explicit commit direction (S4 re-baseline).** Between rows 5 and 6, Mat directed a commit ("commit", 2026-11-15). HEAD moved from `6813232` to `1e54433`: `4c3c831` holds the triage workstream and both grouping files, and `1e54433` holds Session 84. No working-tree byte changed, `git diff --stat 6813232..HEAD` lists no EDITED path and no file of this plan folder (`rebase-diff-names.txt`), and `VALIDATOR`'s sha256 is unchanged. `rebaseline.py` re-recorded `baseline.sha` as `1e54433a797842f157e7af367ff5fec12f13f78b` and refreshed `baseline-content.txt` and `baseline-dirty.txt`: 7 out-of-scope dirty paths kept their row-0 hashes (the Session 86 and 87 plan files and their plan reviews), and 37 now-committed paths dropped out. `scope-check.py --check` and `s84-landed.py` both pass after it. `hdp-check.py`'s `BASE_DEFAULT` stays `6813232`: §4 and the line-ending baseline compare against the row-0 base, and no EDITED file changed in the two commits.
- **An inventory gap, `issue-triage.md:155`.** The plan's inventory missed the line "web research via the harness `web_search_tool` ladder", which C2 refuses. Row 5 applied I17's substitution to it: "research (the harness `web_search_tool` ladder for the web), then the obviousness test".
- **`current-focus.md`.** After Mat's commit, it holds only committed text. H1-3 added this session's entry on top (two lines and a blank line, CRLF kept) and changed no other line. Session 84's entry is now second and does not yet carry a "committed on `main`" line; that line belongs to Session 84's own closeout.
- **`AC-940` in the AC coverage check.** The first H1-6 and H1-6a runs refused the handoff: `1 plan AC(s) never appear in handoff ...: AC-940`. It is the Zorivest reference `AC-940.4` in the plan's Refs and precedents. A note under the AC table names it; `VALIDATOR` and the plan are unchanged.
- **H1-2 ran once.** The full gate passed on its first run; `py-tests` was `2847 passed` with no failure, so neither the baseline rule nor the `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE` procedure was used, and `known-issues.yaml` was not touched.
- **Receipts and the home folder.** pytest's temp folders were set to `C:\Temp\av-kit\hdp85\tmp` (TMP and TEMP), so no receipt of the gate holds the home prefix; this handoff quotes none.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "hdp-row0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-0.ps1 (task.md row 0 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "Row 0: baseline.sha, baseline-dirty.txt, baseline-content.txt and the EOL snapshot; s84-landed; the base closeout selftest and Session 84 tests (EVIDENCE); uv sync; the base Python suite; the state render; the plan-local selftests; the oracle's Red", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 (baseline.sha) plus the plan folder", "output": "baseline.sha 6813232d8769be71eb6e72505b6f39c58c11bddd; baseline-dirty.txt 55 paths; s84-landed: Session 84 is closed; closeout selftest RESULT: 231 arm(s), 0 failure(s); s84 tests 101 passed; base suite 2847 passed, 37 warnings; state-render Drift check passed; identity selftest 0 failure(s); scope-check selftest 0 failure(s); s84-landed selftest 0 failures; hdp-check selftest 0 failures; hdp-red exit=1 (must be 1): C1 FAIL (1), C2 FAIL (38), C3 FAIL (63), C4 FAIL (29), C11 FAIL (1), hdp-check: 132 failure(s); baseline: all steps as expected"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-row1-protocol", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-1.ps1 (task.md row 1 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "Row 1: the protocol rewrite and validator-binding.json (AC-1 to AC-10)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus row 1", "output": "hdp-check.py --checks C3,C6,C11 with the binding and both EVIDENCE receipts: C3 ok, C6 ok, C11 ok; hdp-check: all checks pass"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-row2-templates", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-2.ps1 (task.md row 2 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "Row 2: the four templates and their twins (AC-13)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 and 2", "output": "C4 ok, C5 ok, C6 ok, C9 ok; hdp-check: all checks pass; VALIDATOR --selftest RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms]; template-mode task lint OK: 19 row(s)"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-row3-agents", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-3.ps1 (task.md row 3 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "Row 3: AGENTS.md:27 and the rule-preservation postimage digest (AC-11)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 3", "output": "C4 ok, C6 ok, C7 ok; hdp-check: all checks pass; test_framework_adoption.py 91 passed"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-row4-delegation", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-4.ps1 (task.md row 4 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "Row 4: the model-delegation.md Open decisions bullet (AC-12)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 4", "output": "C4 ok, C6 ok; hdp-check: all checks pass"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-row5-workflows", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-5.ps1 (task.md row 5 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "Row 5: the nine workflow files, I8 to I16 (AC-14, AC-16)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 5", "output": "C2 ok, C4 ok, C6 ok; hdp-check: all checks pass"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-rebaseline", "command": "python C:/Temp/av-kit/hdp85/rebaseline.py > C:/Temp/av-kit/hdp85/rebaseline.txt; then scope-check.py --check and s84-landed.py", "cwd": "P:/av-kit", "scope": "The S4 re-baseline after Mat's directed commits 4c3c831 and 1e54433 (between rows 5 and 6)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1e54433 plus rows 1 to 5", "output": "HEAD 1e54433a797842f157e7af367ff5fec12f13f78b; kept dirty 7, dropped (now committed, clean) 37; baseline-dirty.txt paths 32; scope-check: ok (scope-post-rebaseline.txt); s84-landed: Session 84 is closed (s84-landed-post-rebaseline.txt)"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-row6-docs", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-6.ps1 (task.md row 6 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "Row 6: five docs and two skills, I17 to I23 (AC-15, AC-16, AC-17)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1e54433 plus rows 1 to 6", "output": "C1 ok, C2 ok, C6 ok, C8 ok, C10 ok; hdp-check: all checks pass"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-row7-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-7.ps1 (task.md row 7 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "Row 7: the oracle with every check, the binding and both EVIDENCE receipts; its selftest; scope-check (AC-1 to AC-19)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1e54433 plus rows 1 to 6", "output": "C1 to C11 ok, hdp-check: all checks pass (hdp-green.txt); hdp-check selftest: 0 failures (hdp-selftest.txt); scope-check: ok (hdp-scope.txt)"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-h1-1-unchecked", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-H1-1.ps1 (task.md row H1-1 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "H1-1: no implementation row left unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1e54433 plus rows 1 to 7", "output": "unchecked implementation rows: []"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-hdp-v2-protocol/session-gate.ps1 *> C:/Temp/av-kit/hdp85/hdp-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/hdp85/hdp-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code (task.md row H1-2 Validation cell, verbatim, run as C:/Temp/av-kit/hdp85/row-H1-2.ps1 from P:/av-kit; first run)", "cwd": "P:/av-kit", "scope": "H1-2, the D6 gate on the whole tree after rows 0 to 7: identity before; static tools-lint, task-contract, task-template, scope-paths, hdp-check (binding and evidence), hdp-check-selftest, scope-check-selftest, s84-landed-selftest; targeted adoption and closeout-selftest; fresh full py-tests and state-render; identity after. py-lint/py-types, ui-*, mcp-*, openapi and build-record skipped with their reasons", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "1e54433a797842f157e7af367ff5fec12f13f78b+5bda8cbf0923ccd76a6447b50e9dd7465f6e526ce301a68c6c009897ce8b3348", "output": "first run, no rerun. tested_state before=1e54433a797842f157e7af367ff5fec12f13f78b+5bda8cbf0923ccd76a6447b50e9dd7465f6e526ce301a68c6c009897ce8b3348 after=1e54433a797842f157e7af367ff5fec12f13f78b+5bda8cbf0923ccd76a6447b50e9dd7465f6e526ce301a68c6c009897ce8b3348; tools-lint All checks passed!; task-contract OK: 25 row(s), 23 fully checked, 2 exempt (view_file): H1-5, H2-1; task-template OK: 19 row(s); scope-paths scope-check: ok; hdp-check C1 to C11 ok, all checks pass; hdp-check selftest: 0 failures; scope-check selftest: 0 failure(s); s84-landed selftest: 0 failures; adoption 91 passed in 55.11s; closeout-selftest RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms]; py-tests 2847 passed, 37 warnings in 190.19s; state-render Drift check passed (153 MEUs, 12 phases); session-gate: all steps exit 0"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-h1-3-render", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-H1-3.ps1 (task.md row H1-3 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "H1-3: the current-focus entry, then the SSOT render check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "1e54433a797842f157e7af367ff5fec12f13f78b+5bda8cbf0923ccd76a6447b50e9dd7465f6e526ce301a68c6c009897ce8b3348 (current-focus.md is not an identity input)", "output": "Drift check passed — SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content"}
```
```json
{"schema_version": "evidence.v1", "check_id": "hdp-h1-4-openapi", "command": "pwsh -NoProfile -File C:/Temp/av-kit/hdp85/row-H1-4.ps1 (task.md row H1-4 Validation cell, verbatim, written by C:/Temp/av-kit/hdp85/rowcmd.py)", "cwd": "P:/av-kit", "scope": "H1-4: the basis for skipping the OpenAPI check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 1e54433 plus rows 1 to 7", "output": "packages/api changes: []"}
```

### Quality Gate Results

`hdp-gate-h1-2` is the fresh full record, and its last line is:

> session-gate: all steps exit 0

| Step | Stage | Result |
|------|-------|--------|
| identity-before / identity-after | identity | `tested_state` `1e54433a797842f157e7af367ff5fec12f13f78b+5bda8cbf0923ccd76a6447b50e9dd7465f6e526ce301a68c6c009897ce8b3348` both times |
| tools-lint | static | `All checks passed!` (ruff on `hdp-check.py`, `scope-check.py`, `s84-landed.py`) |
| task-contract | static | `OK: 25 row(s)`; 23 fully checked; 2 exempt (`view_file`): H1-5, H2-1 |
| task-template | static | `OK: 19 row(s)`; 13 fully checked; 4 placeholder-command and 2 `view_file` rows exempt (D-857) |
| scope-paths | static | `scope-check: ok` |
| hdp-check | static | C1 to C11 `ok`; `hdp-check: all checks pass` |
| hdp-check-selftest | static | `hdp-check selftest: 0 failures` |
| scope-check-selftest | static | `scope-check selftest: 0 failure(s)` |
| s84-landed-selftest | static | `s84-landed selftest: 0 failures` |
| adoption | targeted | `91 passed in 55.11s` |
| closeout-selftest | targeted | `231 arm(s), 0 failure(s) [96 must-OK arms]` |
| py-tests | full | `2847 passed, 37 warnings in 190.19s`; no failure, so the baseline rule excused nothing |
| state-render | full | `Drift check passed`, 153 MEUs, 12 phases |
| py-lint/py-types, ui-*, mcp-*, openapi, build-record | skipped | nothing under `packages/`, `tests/`, `ui/` or `mcp-server/` changes; no `packages/api` change (H1-4); no build |

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `.agent/docs/human-decision-protocol.md` | modified | The v2 protocol (row 1); 306 lines, CRLF |
| `AGENTS.md` | modified | Line 27, the decide-before-you-ask rule; 126 lines, CRLF |
| `docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md` | modified | The `AGENTS.md` postimage digest |
| `.agent/templates/PLAN-TEMPLATE.md`, `TASK-TEMPLATE.md`, `HANDOFF-TEMPLATE.md`, `REFLECTION-TEMPLATE.md` and their twins `docs/execution/plans/PLAN-TEMPLATE.md`, `docs/execution/plans/TASK-TEMPLATE.md`, `.agent/context/handoffs/TEMPLATE.md`, `docs/execution/reflections/TEMPLATE.md` | modified | Brief v2, `mandatory:`, the reflection link list, the handoff Decision Log form; twins byte-identical |
| `.agent/docs/model-delegation.md` | modified | The `Open decisions` bullet (2 lines, CRLF); line 5 stays bare LF |
| `.agent/workflows/create-plan.md`, `session-grouping.md`, `execution-session.md`, `issue-triage.md`, `next-project.md`, `meu-handoff.md`, `delegated-plan-creation.md`, `inspiration-research.md` (`:158` only), `tdd-implementation.md` | modified | Row 5, I8 to I16 |
| `.agent/docs/issue-lifecycle-guide.md`, `commands.md`, `development-lifecycle.md`, `emerging-standards.md`, `cloud-local-collaboration.md`; `.agent/skills/completion-preflight/SKILL.md`, `.agent/skills/cli-dispatch/SKILL.md` | modified | Row 6, I17 to I23; the lifecycle boxes keep their widths |
| `.agent/context/current-focus.md` | modified | This session's entry on top; CRLF kept |
| Plan folder: `baseline.sha`, `baseline-dirty.txt`, `baseline-content.txt`, `eol-baseline.json`, `validator-binding.json`, `session-gate.ps1` (new at H1-2, LF), `task.md` (rows marked), `implementation-plan.md` and `hdp-check.py` (D-856) | new or modified | The plan's records, oracle and gate |

All 28 EDITED files keep their row-0 line endings (C6): 27 are pure CRLF and `model-delegation.md` has its one bare LF on line 5. `git diff --stat HEAD`: 28 files changed, 241 insertions, 218 deletions (before H1-3).

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| §5a, the expert-pass skill, the peer-reviewer agent and the §6 hand-over rule | deferred | Session 86 `hdp-expert-pass` | Grouping D-821; Session 86 next edits `PROTOCOL`, `model-delegation.md` and `commands.md`, anchored on §4a (M-3, M-5, M-6, M-8), the M-3 note, the §6 overturn paragraph and the `Open decisions` bullet |
| The rest of `inspiration-research.md` and `.agent/skills/git-workflow/SKILL.md` | deferred | Session 87 `framework-small-syncs` | Session 87 binds to the content this session leaves; only the `Topic too broad` row differs from HEAD |
| Commit and push | out-of-scope | — | Only on Mat's direction, after Codex approves |

**Flags for Mat.** `current-focus.md` is shared: Session 85's entry was added on top of committed text, and Session 84's entry has no "committed" line yet. Session 86 edits `PROTOCOL`, `model-delegation.md` and `commands.md` next, so those three files will move again after this review.

---

## Decision Log

```yaml
decision_log:
  - id: D-856
    stage: execution
    question: "Should §6 state that the closeout validator reads a double-quoted value after decoding its escapes (plan review R2 Q3 note), and should the oracle bind that clause?"
    resolution: human
    class: governance-value
    mandatory: [M-8]
    chosen: "Yes: extend S6_VALIDATOR with the clause, add a dq-escapes topic to ORACLE.TOPICS bound to the five decision-escaped-* selftest arms, and update the plan's quote, topic table and count (25 topics)"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-11-15-hdp-v2-protocol/implementation-plan.md:91 — the binding has one entry per ORACLE.TOPICS topic", "tools/validate_closeout_artifacts.py (Session 84) — decodes double-quoted escapes, so a quoted newline is blank"]
    research: { engine: none, sources: [] }
    reasoning: "The plan says §6 describes what the Session 84 validator checks, and Session 84 refuses a double-quoted blank such as a quoted newline; leaving the clause out would make §6 describe a weaker check than the one that runs. Adopting a reviewer note into the acceptance oracle is M-8, so it went to the human; leaving §6 as planned lost because the omission would be found again in review."
    human_message_reference: 'USER_EXPLICIT 2026-11-15 "Run HDP on any decisions that come up and and I approving acceptance of the defaults."'
  - id: D-857
    stage: execution
    question: "The template-mode task lint fails at HEAD without --allowed-builder-classes; how should the gate run it?"
    resolution: autonomous
    class: two-way
    chosen: "Pass --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier, the same flag the task-contract step and the peer gates use"
    source_tag: Local Canon
    precedents: ["C:/Temp/av-kit/hdp85/lint-head-template-noflag.txt — HEAD's template refused: builder_model 'avkit_builder' is not a capability class", "C:/Temp/av-kit/hdp85/lint-head-template-flag.txt — OK: 19 row(s) with the flag"]
    research: { engine: none, sources: [] }
    reasoning: "The refusal is about the av-kit builder class names, not this session's edit, and the lint itself names the flag; running without it would fail on a base fact, and editing the template's builder column is outside the plan."
  - id: D-858
    stage: execution
    question: "C4 needs session-grouping.md to hold GROUPING_HEADER with plain pipes, but inside a table cell the pipes must be escaped; where does the header go?"
    resolution: autonomous
    class: two-way
    chosen: "Write the header out, unescaped, on its own line below the table, as 'Row 8's table header, without the table escapes'"
    source_tag: Local Canon
    precedents: [".agent/workflows/session-grouping.md — the row 8 column table"]
    research: { engine: none, sources: [] }
    reasoning: "It meets C4 without changing the oracle and gives agents a header they can copy; changing the oracle to accept escaped pipes lost because the oracle is the plan's fixed acceptance check."
  - id: D-859
    stage: execution
    question: "The plan's wording for execution-session.md:284 would repeat 'recommendation first'; replace the dropped clause or drop it?"
    resolution: autonomous
    class: two-way
    chosen: "Drop 'and what happens without an answer'; the line reads 'recommendation first, and the options with a do-nothing option.'"
    source_tag: Local Canon
    precedents: [".agent/docs/human-decision-protocol.md §5 — a brief says what happens without an answer only when something else happens"]
    research: { engine: none, sources: [] }
    reasoning: "The plan's literal replacement adds 'and the recommendation' right after 'recommendation first', which says the same thing twice; dropping the clause keeps the meaning and removes the stale phrase C2 looks for."
  - id: D-888
    stage: execution
    question: "completion-preflight/SKILL.md:163's second sentence still says the closeout reconciles the Decisions Log against the stage logs, which Session 84 removed; correct it?"
    resolution: autonomous
    class: two-way
    chosen: "Rewrite it to say the --decision-source flags read the stage logs, refuse an entry with a blank question, chosen option or reasoning, and refuse the Decisions Log only when the template's example line is left in place"
    source_tag: Local Canon
    precedents: [".agent/docs/human-decision-protocol.md §6 — S6_VALIDATOR's clauses", "tools/validate_closeout_artifacts.py — check_decisions_log(sources, issues) and EXAMPLE_CHECK (Session 84)"]
    research: { engine: none, sources: [] }
    reasoning: "Keeping the old sentence would leave a skill describing a check that no longer runs, the drift this session removes; the new text states only what §6 and the validator now do."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-15 | claude-code-local (Claude Opus 5.5) | Initial handoff after H1-2 (gate run 1), H1-3 and H1-4 |
