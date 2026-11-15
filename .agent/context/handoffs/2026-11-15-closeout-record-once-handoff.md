---
date: "2026-11-15"
project: "2026-11-15-closeout-record-once"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-closeout-record-once/implementation-plan.md"
build_plan_section: "none (closeout tooling; no MEU, D-821)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-15-closeout-record-once-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. This is closeout tooling with no MEU (D-821), Session 84 of the HDP v2 and framework sync grouping (`.agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md`). It ports two `P:/agentic-framework` commits into `tools/validate_closeout_artifacts.py`:

- **`a73d6df`, the closeout-validator part only (record once).** The closeout reads each decision once, where it was made: the plan, the handoff, the plan's declared grouping, or an issue named by `--decision-issue`.
  - An entry whose `question`, `chosen` or `reasoning` is blank or not text is refused (`decision_field_text`, `_NON_TEXT_SCALAR`; AC-3, AC-4).
  - A `chosen` that starts with `pending` is refused (`is still pending`; AC-2).
  - The reflection-versus-stage-log reconciliation is removed: `check_decisions_log` now takes `(sources, issues)` and the reflection no longer restates each decision (D-826; AC-7).
  - `EXAMPLE_CHECK`: a reflection whose Decisions Log still holds the template example line is refused (AC-6).
- **`ec3857a` (the repository boundary).** `project_root` stops its ancestor search at an ancestor with a `.git` entry, a folder or a file (AC-9, AC-10). This closes known issue `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` (AC-12, AC-17).

The av-kit deviations from upstream, each planned and sourced:

- `_quoted_scalar_text` reads a quoted value by YAML's rules: a trailing `# comment` after the closing quote is dropped, and a double-quoted value's escapes are decoded through `DQ_ESCAPE_VALUES` (D-831, amended after R1 and its recheck; CRO-P1, CRO-R1-1). Upstream's `_unquote` call is the defect it replaces.
- `grouping_row_problems` checks a grouping row: a ruled row needs its Question, Chosen and Reasoning cells, and a `pending` Chosen is refused; an `open` row needs its Reasoning (D-829, amended after R1; CRO-P2).
- The selftest went from 219 arms (67 must-OK) to 231 arms (96 must-OK): 14 removed, 16 flipped, 26 added (12 from `UPSTREAM_A`, 3 repository-boundary arms from `UPSTREAM_E`, 6 after plan review R1, 5 after the R1 recheck), with the two rewrites (D-836).

Not ported, per the plan's §Out of Scope: the protocol, templates, expert pass and hand-over parts of `a73d6df` (Sessions 85 and 86), and upstream's `_stage_*` framework. Nothing ships; these are repository tools.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-closeout-record-once/implementation-plan.md). Codex approved the plan at round 2 of 3 (`.agent/context/handoffs/2026-11-15-closeout-record-once-plan-critical-review.md`). **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, "proceed with orchestrating plan creation from session 84 to 87. Create plans in paralell where posible. Then execute the plans in squence. Run HDP on any decisions that come up and and I approving acceptance of the defaults." That acceptance does not cover commit, push, merge, release, destructive data operations, external disclosure or credentials (S10).

**For Mat:**

- **D-838.** The old stage logs hold 2 open problem entries that the ported validator refuses: D-246 and D-251 in `docs/execution/plans/2026-11-04-rc2-ffmpeg-uninstall/`, whose `chosen` is still pending. That plan's own closeout records the rulings (plan §Out of Scope); nothing here changes them.
- **Shared files.** `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` and `.agent/context/current-focus.md` also hold the triage workstream's uncommitted hunks (`baseline-dirty.txt`). This session changed only `known-issues.yaml`'s `.issues[89]` (5 fields, through `issue-resolve.py`) and its new last entry `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE` (through issue_triage's `add_issue`), the two issues' rows and the totals line in the rendered `known-issues.md`, and the new top entry of `current-focus.md`. You choose whether to commit them together or stage by hunk (H2-5).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | integration | A plan decision stated in full, with `reasoning` as a `\|` block scalar, is read; the CLI exits 0 with a table-form reflection | Spec (`UPSTREAM_A`) | `tests/tooling/test_closeout_record_once.py:148` (CLI by subprocess) | ✅ |
| AC-2 | integration | A `chosen` that starts with `pending` exits 1 with `is still pending`: plan, handoff, issue, commented, escaped and grouping-row cases; `Keep the pending queue`, `Pendingly`, `Keep # 3` and an `open` grouping row exit 0 | Spec (`UPSTREAM_A`); Local Canon (D-829, D-831) | `test_closeout_record_once.py:170` (parametrized), `:176`, `:184`, `:190`, `:209` (parametrized), `:215` | ✅ |
| AC-3 | integration | A blank or non-text `chosen` or `question` exits 1, including commented and escaped blanks and blank grouping cells; `3 rounds`, escaped text and a grouping Chosen `49` exit 0 | Spec (`UPSTREAM_A`; Zorivest AC-942.4); Local Canon (D-829, D-831) | `test_closeout_record_once.py:246` (parametrized), `:260` (parametrized), `:273` (parametrized), `:279` | ✅ |
| AC-4 | integration | A blank `reasoning` exits 1, including `"" # later`, an issue's `"\n"` read through `--decision-issue`, and a blank grouping Reasoning cell; a one-word reasoning and a single-quoted `\n` exit 0 | Spec (`UPSTREAM_A`); Local Canon (D-829, D-831) | `test_closeout_record_once.py:298` (parametrized), `:304`, `:345` (parametrized), `:358` (parametrized) | ✅ |
| AC-5 | integration | The repeatable `--decision-issue`: a pending D-9 is refused naming `OTHER-ISSUE`; two issues give `3 stage-log decision(s) read`; one gives `2 stage-log decision(s) read, each stated in full`; a repeated ID is `USAGE`, exit 2; an absent issue is refused beside a present one | Local Canon (D-283, D-828) | `tests/tooling/test_closeout_register_grammar.py:267`, `:279`, `:286`, `:293` | ✅ |
| AC-6 | integration | `EXAMPLE_CHECK`: the template example line exits 1 with `still holds the template example`; a link list and `None.` exit 0 | Spec (`UPSTREAM_A`) | `test_closeout_record_once.py:375` (parametrized) | ✅ |
| AC-7 | integration | A `None.` reflection and a link-list reflection each exit 0 while the plan, the handoff, the declared grouping and an issue all record decisions; a pending plan `chosen` still exits 1 | Human-approved (D-826) | `test_closeout_record_once.py:404` (2 cases), `:409` | ✅ |
| AC-8 | integration | The kept checks still refuse: one ID with two stages, a repeated ID in each source kind, an undeclared `grouping_source`, an `UNFILLED` marker, a missing template section | Local Canon (D-827, D-829) | `test_closeout_record_once.py:418`, `:426` (4 cases), `:449`, `:471` (parametrized) | ✅ |
| AC-9 | unit | `project_root` stops at a `.git` folder or file, and finds `.agent` and `.git` in one repo root or in the plan's own folder | Spec (`UPSTREAM_E`) | `test_closeout_record_once.py:510` (4 cases) | ✅ |
| AC-10 | integration | A plan inside a `.git` folder that declares `grouping_source: "demo.md"` is refused with the outer `.agent` folder's `demo.md`, and read with the repo's own | Spec (`UPSTREAM_E`) | `test_closeout_record_once.py:529`, `:535` | ✅ |
| AC-11 | unit | `--selftest` with `TMP` and `TEMP` at `C:/Temp/av-kit/cro/tmp` exits 0 with 0 failures; `selftest-arms-check.py` accepts 231 arms, 96 wanting `0/OK`, and the §Selftest arm changes exactly | Human-approved (D-826); Local Canon (D-836) | Row 6 `cro-selftest.txt`, `cro-arms-check.txt`; gate `closeout-selftest`, `arms-check` | ✅ |
| AC-12 | integration | Under the user's own temp folder the selftest exits 0 with `0 failure(s)`, and the adoption test `test_evidence_contract_real_cli_selftests` passes | Local Canon (`CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`; D-822, D-830) | Row 6 `cro-selftest-default-tmp.txt`, `cro-adoption.txt`; gate `closeout-selftest-default-tmp` | ✅ |
| AC-13 | integration | No reflection the base validator accepts is refused by the ported one, and none is refused for the template example | Local Canon | Row 8 `reflections-check.py` (`cro-reflections.txt`); gate `reflections-check` | ✅ |
| AC-14 | integration | `stage-log-survey.py --compare` against row 0's receipt: the same 29 problem entries, 2 open, and 0 grouping rows over 10 groupings | Local Canon (D-829, D-831) | Row 8 `cro-survey.txt`; gate `survey-compare` | ✅ |
| AC-15 | unit | `port-check.py` accepts `PORT_SHAPE`, the av-kit deviations, every `QUOTED_PROBES` answer and the docstring phrases | Spec (`UPSTREAM_A`, `UPSTREAM_E`); Local Canon (D-827, D-828, D-833) | Rows 5 and 7 `cro-port-check.txt`, `cro-port-check-register.txt`; gate `port-check` | ✅ |
| AC-16 | unit | `VALIDATOR` and `test_closeout_register_grammar.py` are only CRLF; `test_closeout_record_once.py`, `known-issues.yaml` and `known-issues.md` have no CRLF | Local Canon | `port-check.py` line-end read (rows 5 and 7, gate) | ✅ |
| AC-17 | integration | `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is `resolved` with `verification` and `resolution_path`; `issue-resolve.py` reports no other parsed difference; `issue_triage.py render --check` exits 0 after `render` | Local Canon (D-822, D-834) | Row 7 `cro-issue-resolve.txt`, `cro-issues-render.txt`, `cro-issues-render-check.txt`; gate `issues-render-check` | ✅ |
| AC-18 | static | `ruff check tools/validate_closeout_artifacts.py tests/tooling/` is clean, and the full Python suite fails no test that row 0's receipt shows passing | Local Canon (D-837) | Gate `tools-lint`, `py-tests` (run 3) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-2, AC-3, AC-4 (the refusals) | `assert (1, False) == (1, True)`: the base validator exits 1, but on the reflection reconciliation, not with `is still pending` or `has a blank or non-text ...` | pass | `test_closeout_record_once.py:170-358` |
| AC-2 to AC-4, AC-7 (the passes) | `REFUSE: reflection ... Decisions Log says None. but 1 decision(s) are recorded elsewhere` and `... must be 'None.' or the canonical template table` | pass | `test_closeout_record_once.py:209`, `:273`, `:358`, `:404` |
| AC-6 | the example line is accepted (`assert 1 == 0` on the inverse) | pass | `test_closeout_record_once.py:375` |
| AC-9 | `assert WindowsPath('<the outer folder>') == WindowsPath('<the outer folder>/repo')`: the walk passes the `.git` entry | pass | `test_closeout_record_once.py:510` |
| AC-10 | the outer decoy is read as the declared grouping (exit 0 where 1 is wanted) | pass | `test_closeout_record_once.py:529` |
| AC-5 `test_ac_4`, `test_ac_7` | `assert '3 stage-log decision(s) read' in 'OK: ... 3 recorded decision(s) reconciled against 3 Decisions Log row(s)'`; the pending D-9 is not refused | pass | `test_closeout_register_grammar.py:267`, `:293` |

Row 1's Red was `53 failed, 13 passed in 6.39s` (`cro-red.txt`); `red-check.py` required 7 test ids and found 0 problems (`cro-red-check.txt`). The 13 that passed in Red are guards and negatives that already held (AC-1, most of AC-8, AC-10's repository case and the stated-text negatives). Row 2's Red was `2 failed, 33 passed in 21.21s` (`cro-red-grammar.txt`), the two being `test_ac_4` and `test_ac_7`; `red-check.py` required both and found 0 problems (`cro-red-grammar-check.txt`).

Green: row 3 `92 passed, 9 deselected` (`cro-green-fields.txt`), row 4 `95 passed, 6 deselected` (`cro-green-example.txt`), row 5 `101 passed` (`cro-green.txt`) and `port-check: 0 problem(s)` (`cro-port-check.txt`).

Receipts, all under `C:/Temp/av-kit/cro/`:
- `cro-baseline.txt` and `cro-base-py.txt` (row 0);
- `cro-red.txt`, `cro-red-check.txt`, `cro-red-grammar.txt`, `cro-red-grammar-check.txt` (rows 1 and 2);
- `cro-green-fields.txt`, `cro-green-example.txt`, `cro-green.txt`, `cro-port-check.txt` (rows 3 to 5);
- `cro-selftest.txt`, `cro-arms-check.txt`, `cro-selftest-default-tmp.txt`, `cro-adoption.txt`, `cro-tooling.txt` (row 6);
- `issue-resolve-set.json`, `cro-issue-resolve.txt`, `cro-issues-render.txt`, `cro-issues-render-check.txt`, `cro-port-check-register.txt` (row 7);
- `cro-reflections.txt`, `cro-reflections-run.txt`, `cro-survey.txt`, `cro-survey-run.txt` (row 8);
- `task-unchecked.txt` (H1-1); `cro-gate-h1.txt` and `cro-D6-<step>.txt` (H1-2), with the first run kept as `cro-gate-h1-run1.txt` and `cro-D6-py-tests-run1.txt`;
- `cro-gate-h1-run2.txt`, `cro-D6-py-tests-run2.txt` and `run/rowH1-2-run2.out` (H1-2 run 2); the flake probes `cro-h12-flake-probe-1.txt` to `-3.txt`, `cro-h12-flake-probe-file.txt`, `cro-h12-flake-probe-integration.txt` and `cro-h12-flake-probe-repeat.txt`; the registration `cro-flake-add.txt`, `cro-flake-render.txt`, `cro-flake-render-check.txt`, `cro-flake-md-diff.txt` and `cro-port-check-flake.txt`; and the register copies taken before it, `known-issues-before-flake.yaml` and `known-issues-md-before-flake.md`;
- `cro-render-check.txt` (H1-3) and `openapi-check.txt` (H1-4).

Each row ran its task.md Validation cell verbatim, written by `C:/Temp/av-kit/cro/run/make_row_ps1.py` into `C:/Temp/av-kit/cro/run/row<id>.ps1` after the row environment (`Set-Location P:/av-kit`, `PYTHONIOENCODING=utf-8`, `RECEIPTS_DIR=C:/Temp/av-kit`), and run as `pwsh -NoProfile -File` with its output in `row<id>.out`. Before each Green step `C:/Temp/av-kit/cro/run/s4_check.py` checked S4 (HEAD `6813232`, every changed path in scope or in `baseline-dirty.txt`, every other baseline-dirty path at its row-0 hash); every run reported 0 problems.

**Execution notes.** Each is a deviation from a row's command as written, or from the plan. None changes a check.

- **Row 1:** the AC-2 case `chosen: pending: yes` is written in the test as the quoted string `'"pending: yes"'`, so the YAML value is the text `pending: yes`, which is what the plan's case means (a plain `pending: yes` would be a nested mapping, not a choice).
- **Row 3:** one line of the ported pending check was split in two (`chosen = ...` then `if re.match(r"pending\b", chosen, ...)`) to stay within 100 columns; the logic is upstream's. `port-check.py` accepts it.
- **Row 6:** `ruff format` left one E501 line in the new arm `reflection-decisions-log-example-refused` (the example reflection literal). It was split into two adjacent string literals that join to the same text; `ruff check` is then clean and the arm's want is unchanged.
- **Row 6 to 7:** `make_row_ps1.py 5` was run a second time by mistake and regenerated `row5.ps1` with identical content; nothing ran from it.
- **H1-2, first gate run:** every step through `issues-render-check` exited 0. `py-tests` exited 1 with `1 failed, 2846 passed, 37 warnings in 189.72s`; the failure, `tests/integration/test_video_real_ffmpeg.py::test_ac_134_10_counter_clip_frames_match_a_full_decode` (`ValidationError: frame grab failed at 00:00:02.999`), is outside the row-0 baseline, which passed it. Nothing in this session touches video code, and the file is unchanged since `2832e3d`. Run alone with the gate's environment it passed 3 of 3 times (`cro-h12-flake-probe-1.txt` to `-3.txt`: `1 passed in 9.25s`, `1.36s`, `7.50s`), so it looked like a timing flake under load from the parallel sessions on this machine. The first run's receipts were kept and the gate was rerun from the start. `state-render` and `identity-after` were `not_run` in the first run.
- **H1-2, second gate run:** the same result. Every step through `issues-render-check` exited 0, and `py-tests` exited 1 with `1 failed, 2846 passed, 37 warnings in 188.81s`, the same test failing at `00:00:02.999`; `state-render` and `identity-after` were `not_run`. Probes after it (`cro-h12-flake-probe-file.txt`, `-integration.txt`, `-repeat.txt`): the test file alone failed once (`1 failed, 20 passed in 5.90s`, the same test) and then passed 6 of 6 times (`21 passed`); `tests/integration/` failed once on a sibling, `test_ac_134_10_long_audio_past_the_last_frame` (`frame grab failed at 00:00:03.200`). The failure is nondeterministic and sits on end-of-clip frame grabs in `CaptureService.frames_from_video`; nothing this session changes is imported by that code, `packages/` is unchanged, and `packaging/ffmpeg-win64/` is unchanged since 2026-10-31. **H1-2 is not marked**: its receipt does not show `session-gate: all steps exit 0`, and AC-18 is not met by run 2.
- **Deviation, the coordinator's ruling after run 2.** The coordinator chose, as a two-way choice that follows repo precedent (`CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` and the `E2E-*-FLAKE` entries in `known-issues.yaml`; Session 35's H1-2 rerun after an out-of-scope flake), to register the flake and rerun the full gate once, with no HDP brief. Before registering, no later row or gate step was found to bind row 7's register hash: `identity.py` hashes the register into `tested_state`, which the gate measures fresh; `port-check.py` reads only its line endings; S4 checks only that the path is in scope. The issue `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE` (open, low, core, MONITORING, P4) was added through issue_triage's own `add_issue` and `save` (`C:/Temp/av-kit/cro/run/add_flake.py`, receipt `cro-flake-add.txt`): the `add` CLI has no notes, category or priority options, so its API was called instead of hand-editing. A trial on a copy, then the real file, added 15 lines and removed none; `known-issues.md` changed only in its totals line and the new row (`cro-flake-md-diff.txt`); `render` and `render --check` exit 0 (`cro-flake-render.txt`, `cro-flake-render-check.txt`); `port-check.py` 0 problems (`cro-port-check-flake.txt`).
- **H1-2, third gate run:** `session-gate: all steps exit 0`, with `py-tests` at `2847 passed, 37 warnings in 182.34s` and `tested_state` the same before and after. **AC-18 is met by this fresh passing full run.** A pass on rerun is not a fix: the flake stays open in the register, with the next step to log the frame-grab ffmpeg stderr and the clip duration near the tail on a repeat.
- **Receipts with the raw home prefix.** Three local receipts hold it, from pytest's and the selftest's default temp paths: `cro-red.txt` (row 1), `cro-base-selftest-default-tmp.txt` (row 0) and `selftest-plan-time-default-tmp.txt` (plan time). They are under `C:/Temp/av-kit/cro/`, outside the repository; this handoff quotes no line that holds the prefix, and no tracked file of this plan holds it. They were left as written, because they are evidence other receipts' hashes and `red-check.py` read.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "cro-row0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/cro/run/row0.ps1 > C:/Temp/av-kit/cro/run/row0.out 2>&1 (task.md row 0 Validation cell, verbatim: baseline.ps1 *> C:/Temp/av-kit/cro/cro-baseline.txt; base suite C:/Temp/av-kit/cro/cro-base-py.txt)", "cwd": "P:/av-kit", "scope": "Row 0: baseline.sha, baseline-dirty.txt, baseline-content.txt and baseline-dirty-content.txt; the base validator copy; the selftest arms before; the selftest under both temp folders; uv sync; the base Python suite with TMP and TEMP outside the home folder; the issues render check; the plan-local selftests; the base reflections check and survey", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 (baseline.sha) plus the plan folder", "output": "baseline.sha 6813232d8769be71eb6e72505b6f39c58c11bddd; baseline-dirty.txt 41 paths; differ from HEAD: []; validator crlf 5671 bare-lf 0; selftest 219 arm(s), 0 failure(s) [67 must-OK]; selftest-default-tmp exit=1 (recorded; the known issue) 219 arm(s), 5 failure(s); base suite 2781 passed, 37 warnings in 189.87s; OK: known-issues.md is up-to-date; reflections: 82; both-refuse 34, ok 48; reflections-check: 0 regression(s); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-row1-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/cro/run/row1.ps1 > C:/Temp/av-kit/cro/run/row1.out 2>&1 (task.md row 1 Validation cell, verbatim: uv run pytest tests/tooling/test_closeout_record_once.py *> C:/Temp/av-kit/cro/cro-red.txt with its exit saved; red-check.py *> C:/Temp/av-kit/cro/cro-red-check.txt)", "cwd": "P:/av-kit", "scope": "Row 1: the new test file's Red against the base validator (AC-1 to AC-4, AC-6 to AC-10)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus row 1", "output": "53 failed, 13 passed in 6.39s; red-check: 1 receipt(s), 7 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-row2-red-grammar", "command": "pwsh -NoProfile -File C:/Temp/av-kit/cro/run/row2.ps1 > C:/Temp/av-kit/cro/run/row2.out 2>&1 (task.md row 2 Validation cell, verbatim: uv run pytest tests/tooling/test_closeout_register_grammar.py *> C:/Temp/av-kit/cro/cro-red-grammar.txt with its exit saved; red-check.py *> C:/Temp/av-kit/cro/cro-red-grammar-check.txt)", "cwd": "P:/av-kit", "scope": "Row 2: the grammar file's Red (AC-5), CRLF kept", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 2", "output": "2 failed, 33 passed in 21.21s (test_ac_4_every_named_issue_is_read, test_ac_7_every_decision_present_passes); red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-rows3-5-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/cro/run/row3.ps1, row4.ps1 and row5.ps1, each > C:/Temp/av-kit/cro/run/row<n>.out 2>&1 (task.md rows 3 to 5 Validation cells, verbatim: pytest *> cro-green-fields.txt, cro-green-example.txt and cro-green.txt; port-check.py *> cro-port-check.txt)", "cwd": "P:/av-kit", "scope": "Rows 3 to 5: the field check and the removal, the example check and the wording, the repository boundary; then both test files in full and port-check (AC-1 to AC-10, AC-15, AC-16)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 5", "output": "row 3: 92 passed, 9 deselected in 5.27s; row 4: 95 passed, 6 deselected in 5.26s; row 5: 101 passed in 5.49s; port-check: line ends read for 5 files; port-check: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-row6-selftest", "command": "pwsh -NoProfile -File C:/Temp/av-kit/cro/run/row6.ps1 > C:/Temp/av-kit/cro/run/row6.out 2>&1 (task.md row 6 Validation cell, verbatim: the selftest with TMP elsewhere *> cro-selftest.txt; selftest-arms-check.py *> cro-arms-check.txt; the selftest under the user's own temp *> cro-selftest-default-tmp.txt; the adoption test *> cro-adoption.txt; pytest tests/tooling/ under the user's own temp *> cro-tooling.txt)", "cwd": "P:/av-kit", "scope": "Row 6: the selftest arm changes (AC-11, AC-12)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 6", "output": "RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms]; arms: 231 in the receipt (96 want 0/OK), 219 before, 14 removed, 16 flipped, 26 added; selftest-arms-check: 0 problem(s); default temp RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms]; adoption 2 passed, 89 deselected; tooling 250 passed in 61.68s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-row7-issue", "command": "pwsh -NoProfile -File C:/Temp/av-kit/cro/run/row7.ps1 > C:/Temp/av-kit/cro/run/row7.out 2>&1 (task.md row 7 Validation cell, verbatim: issue-resolve.py with C:/Temp/av-kit/cro/issue-resolve-set.json *> cro-issue-resolve.txt; issue_triage.py render *> cro-issues-render.txt; render --check *> cro-issues-render-check.txt; port-check.py *> cro-port-check-register.txt)", "cwd": "P:/av-kit", "scope": "Row 7: CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR resolved through issue-resolve.py only, and the register rendered (AC-16, AC-17)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 7", "output": "decision logs read: 95 of 95; register sha256 before=dbf960b23813d14877597dfc29a8737f3bf533569a2e2d96e6d2698ef1770d14; target sha256 after=d810ba0a3cc753a38b258bd11f6a6238ffd84a784f5da3091afc38f78ac322c0 CRLF=0 LF=5256; parsed fields changed: 5 (.issues[89] resolution_path, status, verification.last_checked, verification.method, verification.result); issue-resolve: 0 problem(s); Rendered known-issues.md: 65 lines; OK: known-issues.md is up-to-date; port-check: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-row8-old-records", "command": "pwsh -NoProfile -File C:/Temp/av-kit/cro/run/row8.ps1 > C:/Temp/av-kit/cro/run/row8.out 2>&1 (task.md row 8 Validation cell, verbatim: reflections-check.py --before the base copy *> cro-reflections.txt; stage-log-survey.py --compare cro-base-survey.txt *> cro-survey.txt)", "cwd": "P:/av-kit", "scope": "Row 8: old reflections and stage logs under the ported validator (AC-13, AC-14)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 8", "output": "reflections: 82; both-refuse 34, ok 48; reflections-check: 0 regression(s); 278 sources, 1242 entries, 10 groupings; problem-entries: 29; open-problems: 2; kind blank or non-text chosen: 26; kind blank or non-text reasoning: 26; kind still pending: 3; compare with row 0's base survey receipt: 0 difference(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-h1-1", "command": "pwsh -NoProfile -File C:/Temp/av-kit/cro/run/rowH1-1.ps1 (task.md row H1-1 Validation cell, verbatim: the unchecked-row check *> C:/Temp/av-kit/cro/task-unchecked.txt)", "cwd": "P:/av-kit", "scope": "H1-1: no implementation row of task.md is unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 8", "output": "unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-closeout-record-once/session-gate.ps1 *> C:/Temp/av-kit/cro/cro-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/cro/cro-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code (task.md row H1-2 Validation cell, verbatim, run as C:/Temp/av-kit/cro/run/rowH1-2.ps1 from P:/av-kit; third run, after the flake registration)", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 8: identity before; static tools-lint, py-lint, task-contract, scope-paths, port-check, red-check-selftest; targeted record-once-tests, closeout-selftest with TMP elsewhere, arms-check, closeout-selftest-default-tmp, reflections-check, survey-compare, issues-render-check; fresh full py-tests and state-render; identity after. py-types, ui-*, mcp-*, openapi and build-record skipped with their reasons", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "6813232d8769be71eb6e72505b6f39c58c11bddd+c934e95a8a4cd3a17d8cb637affb1100657cf903b2f28a25fdd29a9349b2c54f", "output": "third run (runs 1 and 2 failed py-tests on the out-of-scope VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE; receipts cro-gate-h1-run1.txt, cro-gate-h1-run2.txt). tested_state before=6813232d8769be71eb6e72505b6f39c58c11bddd+c934e95a8a4cd3a17d8cb637affb1100657cf903b2f28a25fdd29a9349b2c54f after=6813232d8769be71eb6e72505b6f39c58c11bddd+c934e95a8a4cd3a17d8cb637affb1100657cf903b2f28a25fdd29a9349b2c54f; tools-lint All checks passed!; py-lint All checks passed!; task-contract OK: 26 row(s), 24 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 51 outside scope: [] baseline-dirty content moved: [] head moved (S4): False; port-check: 0 problem(s); red-check selftest: 36 fixture(s) (11 positive, 25 negative), 0 wrong; record-once-tests 101 passed in 5.35s; closeout-selftest RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms]; arms-check 0 problem(s); closeout-selftest-default-tmp RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms]; reflections-check: 0 regression(s); survey-compare problem-entries 29, open-problems 2, 0 difference(s); issues-render-check OK: known-issues.md is up-to-date; py-tests 2847 passed, 37 warnings in 182.34s; state-render Drift check passed (153 MEUs, 12 phases); session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/cro/cro-render-check.txt (task.md row H1-3 Validation cell, verbatim, run as C:/Temp/av-kit/cro/run/rowH1-3.ps1)", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions after the current focus was updated. No MEU status changes in this session", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "6813232d8769be71eb6e72505b6f39c58c11bddd+c934e95a8a4cd3a17d8cb637affb1100657cf903b2f28a25fdd29a9349b2c54f (current-focus.md and this handoff are outside tested_state)", "output": "Drift check passed: SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "cro-h1-4-openapi", "command": "rtk proxy uv run python -c '<task.md row H1-4: packages/api diff against baseline.sha plus untracked files>' *> C:/Temp/av-kit/cro/openapi-check.txt (run as C:/Temp/av-kit/cro/run/rowH1-4.ps1)", "cwd": "P:/av-kit", "scope": "H1-4: the basis for skipping the OpenAPI check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 6813232 plus rows 1 to 8 (run before the flake registration; packages/api is not in it)", "output": "packages/api changes: []"}
```

### Quality Gate Results

`cro-gate-h1-2` is the fresh full record, and its last line is:

> session-gate: all steps exit 0

| Step | Stage | Result |
|------|-------|--------|
| identity-before / identity-after | identity | `tested_state` `6813232d8769be71eb6e72505b6f39c58c11bddd+c934e95a8a4cd3a17d8cb637affb1100657cf903b2f28a25fdd29a9349b2c54f` both times |
| tools-lint, py-lint | static | `All checks passed!` |
| task-contract | static | `OK: 26 row(s)`; 24 fully checked; 2 exempt (`view_file`): H1-5, H2-1 |
| scope-paths | static | `changed paths: 51 outside scope: [] baseline-dirty content moved: [] ... head moved (S4): False` |
| port-check | static | `port-check: 0 problem(s)` |
| red-check-selftest | static | `36 fixture(s) (11 positive, 25 negative), 0 wrong` |
| record-once-tests | targeted | `101 passed in 5.35s` |
| closeout-selftest (TMP elsewhere) | targeted | `231 arm(s), 0 failure(s) [96 must-OK arms]` |
| arms-check | targeted | `231 in the receipt (96 want 0/OK), 219 before, 14 removed, 16 flipped, 26 added`; 0 problems |
| closeout-selftest-default-tmp | targeted | `231 arm(s), 0 failure(s) [96 must-OK arms]` |
| reflections-check | targeted | 82 reflections, `0 regression(s)` |
| survey-compare | targeted | 29 problem entries, 2 open, `0 difference(s)` |
| issues-render-check | targeted | `OK: known-issues.md is up-to-date` |
| py-tests | full | `2847 passed, 37 warnings in 182.34s`; no failure, so the baseline rule excused nothing |
| state-render | full | `Drift check passed`, 153 MEUs, 12 phases |
| py-types, ui-*, mcp-*, openapi, build-record | skipped | nothing under `packages/`, `ui/` or `mcp-server/` changes; no `packages/api` change (H1-4); no build |

This is the gate's third run. Runs 1 and 2 failed only at `py-tests`, on the out-of-scope flake below; they are kept as `cro-gate-h1-run1.txt` and `cro-gate-h1-run2.txt`.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `tools/validate_closeout_artifacts.py` | modified | The port: `DQ_ESCAPE_VALUES` (`:860`), `_NON_TEXT_SCALAR` (`:1313`), `_quoted_scalar_text` (`:1325`), `decision_field_text` (`:1370`), the field and pending checks in `decision_entries` (`:1429`), `grouping_row_problems` (`:1630`) called from `grouping_decisions` (`:1651`), `project_root`'s `.git` stop (`:1897`), `check_decisions_log(sources, issues)` (`:1940`), `EXAMPLE_CHECK` in `check_reflection` (`:1955`), the removed `reflection_decision_rows` reconciliation, the module docstring and the `--decision-source` help (D-833), the link-list template example (D-839), and the selftest arm changes. +646/−316 lines; 6,001 CRLF lines, 0 bare LF |
| `tests/tooling/test_closeout_record_once.py` | new | AC-1 to AC-4 and AC-6 to AC-10: 66 cases. 538 lines, LF |
| `tests/tooling/test_closeout_register_grammar.py` | modified | AC-5: the fixtures state each decision in full, `run_check` takes a `known_issues` text, `test_ac_4` refuses a pending D-9 naming `OTHER-ISSUE`, `test_ac_7` asserts the new OK lines. +44/−10 lines; CRLF kept |
| `.agent/context/known-issues.yaml` | modified, by `issue-resolve.py` and issue_triage's `add_issue` only | `.issues[89]` `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`: `status: resolved`, `verification` and `resolution_path`; and the new last entry `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE`. LF kept. The file also holds the triage workstream's uncommitted hunks |
| `.agent/context/known-issues.md` | regenerated, by `issue_triage.py render` only | The resolved issue's row leaves the open list; the new flake's row is added and the totals move to 135 (42 active). LF kept. The file also holds the triage workstream's uncommitted hunks |
| `.agent/context/current-focus.md` | modified | This session's entry on top, two lines and a blank line; no other line changed. CRLF kept. The triage workstream's line-1 hunk is untouched |
| Plan folder: `baseline.sha`, `baseline-dirty.txt`, `baseline-content.txt`, `baseline-dirty-content.txt`, `selftest-arms-before.txt`, `session-gate.ps1` (new at H1-2, LF), `task.md` (rows marked) | new or modified | The plan's records and gate |

```diff
--- tools/validate_closeout_artifacts.py: project_root (ec3857a)
     plan = Path(plan_path).resolve()
     for ancestor in plan.parents:
         if (ancestor / ".agent").is_dir():
             return ancestor
+        if (ancestor / ".git").exists():
+            return plan.parent
     return plan.parent
```

```diff
--- tools/validate_closeout_artifacts.py: check_reflection (EXAMPLE_CHECK; record once)
-    # HDP-8: the Decisions Log heading being present says nothing about whether the
-    # decisions made in the plan, the handoffs or the closed issue reached it.
+    # The Decisions Log is a short list of reversible choices with links, or None.
+    # The template's example line left in place is not a list of choices.
+    log = re.search(
+        r"^### Decisions Log\n(?P<body>.*?)(?=^##+ |\Z)", text, re.MULTILINE | re.DOTALL
+    )
+    if log is not None and "_{" in log.group("body"):
+        raise Refuse(
+            f"reflection {path} Decisions Log still holds the template example; list the "
+            f"reversible choices with links, or write None. (human-decision-protocol.md §6)."
+        )
+    # human-decision-protocol.md §6: the stage logs hold the one record of each
+    # decision; read them so a blank, pending or non-text entry is refused.
     if decision_sources_paths:
-        notes.append(check_decisions_log(text, path, decision_sources_paths, decision_issues))
+        notes.append(check_decisions_log(decision_sources_paths, decision_issues))
```

```diff
--- tools/validate_closeout_artifacts.py: decision_field_text, the quoted branch (D-831)
+        if raw[:1] in ('"', "'"):
+            value = _quoted_scalar_text(raw)
+            return value if value is not None and value.strip() else None
+        value = raw.split(" #", 1)[0].strip()
+        if not value or _NON_TEXT_SCALAR.match(value):
+            return None
+        return value
```

```diff
--- tests/tooling/test_closeout_register_grammar.py: test_ac_4 and test_ac_7
-    result = run_check(tmp_path, v._DECISIONS_LOG_ROWS, "OTHER-ISSUE", "CORE-DEMO")
-    assert (result.returncode, "missing decision D-9" in result.stdout) == (1, True), (
+    pending = v._DECISION_KNOWN_ISSUES.replace(
+        'chosen: "Keep"', 'chosen: "pending Mat\'s ruling"', 1
+    )
+    assert pending != v._DECISION_KNOWN_ISSUES
+    result = run_check(
+        tmp_path, v._DECISIONS_LOG_ROWS, "OTHER-ISSUE", "CORE-DEMO", known_issues=pending
+    named = "OTHER-ISSUE" in result.stdout and "still pending" in result.stdout
+    assert (result.returncode, named) == (1, True), result.stdout + result.stderr
-    assert "2 recorded decision(s) reconciled" in single.stdout
+    assert "3 stage-log decision(s) read" in several.stdout
+    assert "2 stage-log decision(s) read, each stated in full" in single.stdout
```

```diff
--- .agent/context/known-issues.yaml: .issues[89] (other fields unchanged)
-    status: open
+    status: resolved
     verification:
-      last_checked: '2026-11-04'
+      last_checked: '2026-11-15'
+      method: 'Session 84 task row 6: the validator selftest run under the user''s own temp folder (receipt cro-selftest-default-tmp.txt) and uv run pytest tests/tooling/ under the same temp folder (receipt cro-tooling.txt), both under C:/Temp/av-kit/cro'
+      result: 'cro-selftest-default-tmp.txt: RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms, so the tool is not refusing everything]. cro-tooling.txt: 250 passed in 61.68s (0:01:01)'
+    resolution_path: 'Fixed in Session 84 on 2026-11-15 (plan docs/execution/plans/2026-11-15-closeout-record-once): project_root ... now stops its ancestor search at the plan''s repository ... ported from agentic-framework ec3857a ...'
```

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
| D-246 and D-251 still pending in `2026-11-04-rc2-ffmpeg-uninstall` | out-of-scope | — | D-838: that plan's own closeout records the rulings; the survey counts them as the 2 open problems |
| The `MEU-72` and `MEU-74` handoffs' Decision Log shape refusal | out-of-scope | — | Closed sessions; the base validator refuses them the same way (survey `other-refusal`) |
| The protocol, templates, expert pass and hand-over parts of `a73d6df` | deferred | — | Sessions 85 and 86 (grouping D-821; D-835) |
| `tests/integration/test_video_real_ffmpeg.py::test_ac_134_10_counter_clip_frames_match_a_full_decode` failed in gate runs 1 and 2 | tracked | `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE` | Registered open (low, P4) on the coordinator's ruling; it passed at baseline, alone 3 of 3, the file alone 6 of 7, and in gate run 3; a sibling failed once in the integration folder; nothing here touches video |
| Commit and push | out-of-scope | — | Only on Mat's direction, after Codex approves (H2-5) |

### Review churn

The plan review's first dispatch, `cro-plan-r1` (2026-11-15T15:21:46Z to 15:33:02Z), returned `changes_required`, but the ledger refused to record it: its blocking finding `CRO-P2` cited `PR-8`, which is not in the loop's registered set (`C:/Temp/av-kit/dispatch/cro-plan-run-r1.txt`: `FAIL: verdict-not-recorded ... no round was consumed`). It used 3,229,394 tokens (3,206,191 input, 3,015,552 of them cached, and 23,203 output; `C:/Temp/av-kit/dispatch/cro-plan-r1/events.jsonl`), which the ledger does not count. The unrecorded review is kept at `C:/Temp/av-kit/cro/cro-plan-review-round-1-unrecorded.md`. The redispatch `cro-plan-r1b` was recorded as round 1 (`changes_required`, 1 blocking, 7,040,891 tokens), and round 2 approved (0 blocking, 8,088,361 tokens).

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-15 | claude-code-local (Claude Opus 5.5) | Initial handoff after H1-2 (gate run 3), H1-3 and H1-4 |
