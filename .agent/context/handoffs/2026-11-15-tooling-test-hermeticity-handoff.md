---
date: "2026-11-15"
project: "2026-11-15-tooling-test-hermeticity"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md"
build_plan_section: "none (tooling tests and their fixtures; no MEU)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-15-capture-inbox-probe-MEU-146-handoff.md"
---

# Handoff: 2026-11-15-tooling-test-hermeticity-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. This is Session 76, the second session of the post-rc.3 triage residuals grouping (`.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md`). It works three tooling issues: `TOOLING-SHARED-REGISTRY-COUPLING`, `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE` and `CLI-DISPATCH-PLACEHOLDER-FIXTURE`.

**Goal anchor:** each tooling test in this scope reads only its own fixture, except one named test that is kept live on purpose. The registry tests resolve against a tracked synthetic registry in a temp registry home. The governance tests check a migrated tree whose rule-map pins and backlinks follow the bytes that tree holds, and one test still checks the tracked rule-map pins against the live instruction files (D-132). The dispatch placeholder arm builds its token at run time. A change to the machine registry, the live governance files or the instantiated project name then no longer reds them, and every assertion they make is unchanged.

**Execution gate.** `plan_to_exec_gate: human`. The plan review approved at round 1 (`.agent/context/handoffs/2026-11-15-tooling-test-hermeticity-plan-critical-review.md`). Mat, 2026-11-15: "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." After the plan review approved, the coordinator wrote those words into the plan's Status line (`implementation-plan.md:15`). That line is the only change made to the plan after its approval.

**Starting tree.** `main` at `3397e78`. Session 75 (`capture-inbox-probe`) is closed and not committed, and the plans and plan reviews of Sessions 77 to 83 are untracked in the same tree. This session left all of them alone. Every check binds to row 0's bytes, not to `HEAD`: row 0 recorded 99 dirty paths with their blobs, and 31 of them outside this scope with their hashes. `HEAD` moved once, after the execution review approved: Mat ordered Session 75 committed, and the coordinator committed it as `661d142` (see the Execution notes).

- **The registry fixture (rows 1 and 2, `TOOLING-SHARED-REGISTRY-COUPLING`).**
  - `tests/tooling/fixtures/registry-home/model-registry.json` (new, LF, 3,804 bytes, 8 catalog entries) is a synthetic registry. `make_fixture.py` beside it (new, LF, standard library only) writes it from the machine registry's shape and the project overlay.
  - `build_registry_home` (`tests/tooling/test_framework_adoption.py:105`) copies the resolver's three tool files from `P:/.agent` (`MACHINE_TOOLS`, `:95`), validates the fixture with `--strict`, and compiles the overlay against it in a temp project. Its environment sets only `AGENT_MODEL_REGISTRY`, to the fixture copy.
  - The five registry tests (16 cases) take the module fixture `registry_home` and resolve with `--project` set to the temp project. `fixture_wrapper` (`:154`) gives the wrapper test a byte copy of `tools/Invoke-CodexDispatch.ps1` whose project-root line points at that project. Every `assert` and `parametrize` list is unchanged (`hermetic-check --asserts`).
- **The governance fixture (rows 3 and 4, `TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE`).**
  - `migrated_tree`'s body moved into `build_migrated_tree(dest, overrides=None)` (`:444`); `migrated_tree` delegates to it.
  - After the copy, `copy_backlink_targets` (`:486`) copies one level of link targets that the copied `AGENTS.md` and `GUARDRAILS.md` name and the tree lacks, by the verifier's own link regex and skip rule. `rebind_instruction_pins` (`:518`) replaces each `postimage_sha256` pin in the copied rule map with the copy's hash, bytewise, each pin asserted unique.
  - `test_ac_14_tracked_rule_map_pin_matches_live_instructions` (`:635`) keeps D-132's signal: it checks the tracked `RULE_MAP` pins against the live files. `tracked_pin_mismatches` (`:530`) gives one message per stale pin, with the rebind command.
- **The dispatch arm (rows 5 and 6, `CLI-DISPATCH-PLACEHOLDER-FIXTURE`).** Arm 2 of `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1` (`:557-571`) builds `{{PROJECT_NAME}}` at run time from braces and its name, under a fresh `cli-dispatch-ph-<guid>` folder in the temp folder. The comment is reworded and three assignment lines changed; every other line, including both `Write-TestResult` lines, is byte for byte the same. The suite now reports 31 PASS and 0 FAIL.
- **Live probe and registers (rows 7 and 8).** `live-probe.py` ran the real machine routes once (AC-12). The register update went through `issue-resolve.py --expect-sha256` and `issue_triage.py render` (AC-13).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | unit | `fixture-check.py` passes on `FIXTURE`: strict validate exit 0 with the copy unchanged; `make_fixture.py` output equal to `FIXTURE`; the key, slug, entry-key, capability-token and string rules; LF and canonical JSON | Local Canon (D-911) | `fixture-check.py` (row 2, gate `fixture-check`); `fixture-check.py --selftest` (row 0) | ✅ |
| AC-2 | integration | `test_ac_2_fixture_registry_home_compiles`: the fixture validates with `--strict`, the overlay compiles against it, the stamp equals `FIXTURE`'s SHA-256, and an `invented` slug fails with `unknown_slug` | Local Canon (D-911); Research-backed (probe-mincap) | `tests/tooling/test_framework_adoption.py:132` | ✅ |
| AC-3 | integration | The four registry tests (13 cases) pass on the fixture and under `HOSTILE`; before row 2 the `RED_IDS` failed under `HOSTILE` by assertion | Local Canon (D-911; TOOLING-SHARED-REGISTRY-COUPLING) | `test_framework_adoption.py:389`, `:407`, `:428`, `:674` (row 1 Red, row 2 and gate `adoption-hostile`) | ✅ |
| AC-4 | integration | `test_review_pipeline_wrapper_refuses_before_provider` (3 cases) runs a temp wrapper copy with `NEEDLE` replaced once; it passes, under `HOSTILE` too, and the fake provider is never called | Local Canon (D-911) | `test_framework_adoption.py:999`, with `fixture_wrapper` at `:154` | ✅ |
| AC-5 | unit | `hermetic-check.py`: `TEST_FILE` CRLF with no BOM; `P:/.agent` once; no `AGENT_MODEL_REGISTRY_HOME` with `P:/`; no `--project ROOT`; the wrapper path only in `fixture_wrapper`; `--asserts` equal to `BASE` | Local Canon (§4a M-7 rows) | `hermetic-check.py --asserts --eol` (rows 2, 4, 6, 8; gate `hermetic-check`); `--selftest` and the run on `BASE` (row 0, exit 1 as required) | ✅ |
| AC-6 | integration | `test_ac_6_pin_follows_the_copied_instructions` passes | Local Canon (D-915; TOOLING-ADOPTION-FIXTURE-LIVE-GOVERNANCE) | `test_framework_adoption.py:605` | ✅ |
| AC-7 | integration | `test_ac_7_backlink_closure_copies_new_targets` passes | Local Canon (D-915) | `test_framework_adoption.py:612` | ✅ |
| AC-8 | integration | `test_ac_8_pin_oracle_still_refuses` passes before and after row 4 | Local Canon (D-915) | `test_framework_adoption.py:623` (row 3 refactor run, row 4 green run) | ✅ |
| AC-9 | integration | The 12 `migrated_tree` cases pass after rows 3 and 4 with unchanged assertions; the `backlink` and `rule-map` mutations still exit 1 | Local Canon (D-915) | `test_framework_adoption.py:559` (×5), `:580` (×5), `:1269` (×2) | ✅ |
| AC-10 | integration | `DISPATCH_TEST` reports FAIL 0 of at least 31, both placeholder names PASS (`--expect-clean`); `--source`: no `{{` in arm 2, BOM and CRLF, both `Write-TestResult` lines and every line outside arm 2's comment and assignments equal to `BASE`, no changed line matching `VERIFIER`'s census patterns | Local Canon (D-913; CLI-DISPATCH-PLACEHOLDER-FIXTURE) | `dispatch-check.py --source` and `--expect-clean` (row 6, gate `dispatch-source`, `dispatch-clean`); `--exact-baseline` (row 5 Red); `--selftest` (row 0) | ✅ |
| AC-11 | integration | `pytest TEST_FILE` on the real tree: 0 failed, passed equals row 0's count plus 5 | Local Canon (session brief) | Gate `adoption-tests` and `adoption-check` (`hermetic-check.py --count`); row 4 `96 passed` | ✅ |
| AC-12 | integration | `live-probe.py` against the real machine registry: the 7 `preserves_bindings` cases from `BASE`, the reviewer route both ways, `--check-compiled` | Local Canon (D-912) | `live-probe.py` (row 7, gate `live-probe`); `--selftest` (row 0) | ✅ |
| AC-13 | integration | Two issues `resolved`, `TOOLING-SHARED-REGISTRY-COUPLING` `mitigated` with its residual, each with `verification` and `resolution_path`; no other parsed difference; `render --check` exits 0; both files LF | Local Canon (the brief: registers through the repo tools) | `issue-resolve.py` (row 8: 13 fields, 3 issues, 0 problems); `issue_triage.py render --check` (row 8, gate `issues-render`) | ✅ |
| AC-14 | integration | `test_ac_14_tracked_rule_map_pin_matches_live_instructions` passes on the real tree; its `tmp_path` half gives exactly one message for one appended byte, holding `AGENTS.md` and the `p.write_bytes(` rebind command | Human-approved (D-132, USER_EXPLICIT 2026-10-27); Local Canon (D-915) | `test_framework_adoption.py:635` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-2 | FAILED: `registry fixture missing: run make_fixture.py beside it` (no `FIXTURE` before row 2) | passed (row 2) | `tests/tooling/test_framework_adoption.py:132` |
| AC-3, AC-4 (the `RED_IDS`, 12 cases) | FAILED by assertion under `HOSTILE`: the live resolver read the hostile registry | passed under `HOSTILE` and in the normal environment (row 2) | `test_framework_adoption.py:389`, `:407`, `:428`, `:999` |
| AC-6 | FAILED: verifier exit 1, `rule map identity mismatch: AGENTS.md` | passed (row 4) | `test_framework_adoption.py:605` |
| AC-7 | FAILED: verifier exit 1, `broken instruction backlink: .agent/docs/fixture-new-policy.md` | passed (row 4) | `test_framework_adoption.py:612` |
| AC-10 (2 PowerShell checks) | `placeholder receipts dir refused` and `refusal created no placeholder dir` FAIL; Total 31, PASS 29, FAIL 2 (row 0 receipt) | Total 31, PASS 31, FAIL 0 (row 6) | `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1:557-571` |

Red, registry (row 1): `13 failed, 4 passed, 75 deselected in 2.93s` (child exit 1), and `red-check: 1 receipt(s), 12 required test(s), 0 problem(s)` with the 12 titles of `red-require.txt` (`RED_IDS`). The four passing cases are the `bad_configuration` validate faults and the `bad-registry` wrapper case, which refuse before they read a registry.

Red, governance (row 3): `2 failed, 93 deselected in 2.97s` (child exit 1), and `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)`. The refactor run in the same row: `13 passed, 82 deselected` (AC-8 and the 12 `migrated_tree` cases). Green (row 4): `16 passed, 80 deselected in 27.87s`; the whole `TEST_FILE` `96 passed in 61.04s`.

Red, dispatch (row 5): row 0's receipt is the Red, `dispatch receipt: Total 31 PASS 29 FAIL 2 SKIP 0; exit 1; FAIL names ['placeholder receipts dir refused', 'refusal created no placeholder dir']`, `dispatch-check: 0 problem(s)` under `--exact-baseline`. Green (row 6): `Total 31 PASS 31 FAIL 0 SKIP 0; exit 0; FAIL names []`.

AC-14 has no Red: the tracked pins match the live files today (row 0: both pins counted once and equal to the live hashes). Its negative is the test's own `tmp_path` half.

Receipts, all under `C:/Temp/av-kit/tth/`:
- row 0: `tth-baseline.txt` (`baseline: all steps exit 0`), `tth-base-py.txt`, `tth-base-adoption.txt`, `tth-base-dispatch.txt` and its `.exit`, `tth-eol-base.txt`; the row-0 copies in `base/`;
- rows 1 and 2: `tth-reg-red.txt` and its `.exit`, `tth-reg-red-check.txt`, `tth-make-fixture.txt`, `tth-fixture-check.txt`, `tth-reg-hostile.txt`, `tth-reg-green.txt`, `tth-hermetic-2.txt`;
- rows 3 and 4: `tth-gov-red.txt` and its `.exit`, `tth-gov-red-check.txt`, `tth-gov-refactor.txt`, `tth-gov-green.txt`, `tth-adoption-4.txt`, `tth-hermetic-4.txt`;
- rows 5 and 6: `tth-dispatch-red-check.txt`, `tth-dispatch-source.txt`, `tth-dispatch-green.txt` and its `.exit`, `tth-dispatch-leftover.txt`, `tth-dispatch-clean.txt`, `tth-hermetic-6.txt`; the first, failed run's receipts are kept as `tth-dispatch-green-noregistry.txt` (and `.exit`) and `tth-dispatch-clean-noregistry.txt` (D-920);
- rows 7 and 8: `tth-live-probe.txt`, `issue-resolve-set-8.json`, `tth-issue-resolve.txt`, `tth-issues-render.txt`, `tth-issues-render-check.txt`, `tth-hermetic-8.txt`;
- each row's S4 check: `tth-scope-1.txt` to `tth-scope-6.txt`;
- H1: `task-unchecked.txt` (H1-1); `tth-gate-h1.txt` (the first run, its step receipts kept under `gate-r1/`) and `tth-gate-h1-r2.txt` with `tth-D6-<step>.txt` (the run after the `HEAD` move) (H1-2); `tth-render-check.txt` (H1-3); `openapi-check.txt` (H1-4); `tth-h15-sources.txt` (H1-5); `handoff-check.txt` (H1-6), `handoff-ac-check.txt` (H1-6a) and `full-evidence-check.txt` (H1-6b).

Each row ran its task.md Validation cell verbatim from `C:/Temp/av-kit/tth/row<n>.ps1`, after the row environment (`Set-Location P:/av-kit`, `PYTHONIOENCODING=utf-8`, `RECEIPTS_DIR=C:/Temp/av-kit`, `ELECTRON_RUN_AS_NODE` cleared) and the S4 check, run as `pwsh -NoProfile -File`.

**Execution notes.** Each is a deviation from the plan, or a fact the plan did not foresee.

- **The Status line.** After the plan review approved, the coordinator wrote Mat's execute words into `implementation-plan.md:15`. It is the only change made to the plan after its approval; no row, AC or decision changed.
- **`red-check.py`'s pytest header (D-919).** pytest pads a failure header with fewer underscores when the test id is long, down to one on each side (`_ test_registry_contract_preserves_bindings[avkit_coordinator-cursor-task-cursor-grok-4.6-xhigh] _`). The copied pattern `^_{3,} (.+?) _{3,}\s*$` missed those headers, so row 1's red-check reported the required tests as missing. The pattern is now `^_+ (.+?) _+\s*$` (`red-check.py:82`), and the selftest gained a long-id fixture: `37 fixture(s) (12 positive, 25 negative), 0 wrong` (`tth-red-check-selftest-2.txt`; the gate's `red-check-selftest` step).
- **Row 6's environment (D-920).** Row 6's first suite run exited 1 with `registry_not_found: no ModelRegistry.psm1 at any S2 location`, because the row command does not set `AGENT_MODEL_REGISTRY_HOME`, which row 0's `baseline.ps1` sets for the same suite. `row6.ps1` set `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, as row 0 did, and the rerun passed. The failed run's receipts are kept under the `-noregistry` names. It created no placeholder folder and did not touch the leftover folder. The gate's `dispatch-tests` step runs with the same environment.
- **`make_fixture.py`'s repository root.** The first draft took `Path(__file__).resolve().parents[3]`, which is `tests/`. It now takes `parents[4]` (`make_fixture.py:41`), the repository root.
- **Lint fixes before placing.** ruff's UP012 flagged an `.encode("utf-8")` in `fixture_wrapper`, now `.encode()`; two E501 lines in `make_fixture.py` were wrapped. No logic changed.
- **`make_fixture.py` was written while row 0 was still running.** It was created after row 0's record step, while the base suite still ran, so `baseline-scope.json` recorded it `absent` correctly. The base suite's collection did not include it (it is not a test module).
- **`baseline.ps1` runs `uv sync` first.** The plan lists `uv sync` as step 6; it runs first so that the collection of step 5 uses the synced environment. The comment at `baseline.ps1:10` says so.
- **`baseline-dirty-blobs.json` is an extra row-0 file.** It records each dirty path's working blob (`git hash-object`), 99 paths. `scope-check.py`'s `HEAD` rule compares a moved path's blob at `HEAD` with that record rather than with the working-file hash: `core.autocrlf` and `text=auto` make the working bytes differ from the blob bytes. This is a stricter form of D-918. It decided the `HEAD` move below: each of the 38 committed paths has the same blob at `661d142` as its row-0 record.
- **Plan-local `__pycache__` folders.** `fixture-check.py` imports `make_fixture.py`, and the gate imports `fixture-check.py`, so Python wrote `__pycache__/` folders beside them. Both are ignored by `.gitignore:3` and were removed after the gate.
- **HOSTILE and temp folders.** `AGENT_MODEL_REGISTRY` was set only in the child of rows 1 and 2 and of the gate's `adoption-hostile` step, each in a `try`/`finally` that set it to `$null`. pytest's temp folders were set to `C:\Temp\av-kit\tth\tmp`; only `dispatch-tests` kept the user's own `TEMP`.
- **The leftover folder is unchanged.** Before and after row 6 and the gate's `dispatch-tests` step: the leftover folder's mtime `2026-11-14T09:21:03` both times, and `cli-dispatch-ph-*` folders 0 before and 0 after. The new arm removes its fresh folder.
- **`HEAD` moved after the execution review (B-1 option 2, D-918).**
  - Mat ordered "yes commit and push" for Session 75. After this session's H1-7 review had approved, the coordinator committed Session 75 as `661d1429a026d39d9a2faacc90fb7ff1ffb95d98` and pushed it to `origin/main`. Neither the executor nor this session made the commit.
  - The commit holds 38 paths. Three of them are files this session also changed: `current-focus.md`, `known-issues.md` and `known-issues.yaml`. They were committed with their row-0 bytes, so this session's changes stay in the working tree and `git diff HEAD` on them now shows only Session 76.
  - `scope-check.py` after the move: `HEAD moved; 38 path(s) changed since baseline.sha`, each one `committed unchanged`, then `scope-check: ok` (`tth-scope-headmove.txt`). Nothing was re-baselined.
  - `tested_state` binds `HEAD`, so it changed from `3397e78…+7763c700…` to `661d142…+df4a25e3…`. The H1-2 gate ran again on the new state and passed (`tth-gate-h1-r2.txt`); `tth-gate-h1-2` below is that run. H1-3, H1-4, H1-6, H1-6a and H1-6b ran again after it.
  - The H1-7 review measured the earlier state, `3397e78…+7763c700…`, before the commit. Its approval covers the same session changes; only `HEAD` differs.
- **`ELECTRON_RUN_AS_NODE` in a manual identity check.** One manual `identity.py --state-only` from a shell that had `ELECTRON_RUN_AS_NODE=1` gave a different state, because the runtime part of the state records that variable. With it unset, the state equals the gate's. Every row wrapper and the gate unset it.
- **This handoff quotes no home-folder path.** Receipts hold full paths; this handoff names the leftover folder only through `$env:TEMP`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "tth-row0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/row0.ps1 (task.md row 0 Validation cell, verbatim: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-tooling-test-hermeticity/baseline.ps1 *> C:/Temp/av-kit/tth/tth-baseline.txt)", "cwd": "P:/av-kit", "scope": "Row 0: uv sync, baseline.sha, the dirty-path records, baseline-scope.json, baseline-api.json, the row-0 copies, the NEEDLE and pin counts, the base Python, adoption and dispatch suites, the dispatch exact-baseline check, the six plan-local selftests, and hermetic-check on BASE (must fail)", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus the row-0 dirty tree", "output": "baseline.sha 3397e78d7342d73e99dde3b43244a55cd6be7e87; baseline-dirty.txt 99 paths; baseline-dirty-hashes.json 31 paths outside this scope; baseline-scope.json 6 paths, 2 absent, known-issues.yaml e451e517aa142eb0d03d67c1dfdddd00aa91f07df4551f124098c0de0fdedce6; baseline-api.json 29 files under packages/api; NEEDLE count in WRAPPER: 1; RULE_MAP AGENTS.md and GUARDRAILS.md pins count 1, live sha256 matches; base suite 2940 passed, 37 warnings in 217.82s; base adoption 91 passed in 57.21s; base dispatch Total 31, PASS 29, FAIL 2 (exit 1), dispatch-exact-baseline exit 0; red-check selftest 36 fixture(s), 0 wrong; identity, dispatch-check, fixture-check, hermetic-check and live-probe selftests 0 failure(s); hermetic-check on BASE: 11 problem(s), exit 1 (must be non-zero); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-row1-registry-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/row1.ps1 (task.md row 1 Validation cell, verbatim: the registry selection under HOSTILE into tth-reg-red.txt, then red-check.py with each red-require.txt title)", "cwd": "P:/av-kit", "scope": "Red for AC-2 to AC-4: build_registry_home and test_ac_2 added, FIXTURE absent, the five tests still live, run under HOSTILE", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus row 1", "output": "13 failed, 4 passed, 75 deselected in 2.93s (child exit 1). red-check: 1 receipt(s), 12 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-row2-registry-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/row2.ps1 (task.md row 2 Validation cell, verbatim: make_fixture.py, fixture-check.py, the selection under HOSTILE in try/finally, the whole TEST_FILE, hermetic-check.py --asserts --eol)", "cwd": "P:/av-kit", "scope": "Green for AC-1 to AC-5: FIXTURE written, the five tests rewired by inputs only", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 1 and 2", "output": "wrote model-registry.json: 3804 bytes, 8 catalog entries; strict validate: exit 0, catalog=8 classes=1 strict=yes; make_fixture.py --out <temp>: bytes equal to FIXTURE: True; independent build equals FIXTURE: True; fixture-check: 0 problem(s); HOSTILE selection 17 passed, 75 deselected in 3.62s; TEST_FILE 92 passed in 55.88s; hermetic-check: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-row3-governance-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/row3.ps1 (task.md row 3 Validation cell, verbatim: -k test_ac_6_ or test_ac_7_ into tth-gov-red.txt, red-check.py --require for both, then the refactor selection into tth-gov-refactor.txt)", "cwd": "P:/av-kit", "scope": "Red for AC-6 and AC-7 after the build_migrated_tree refactor; AC-8 and the 12 migrated_tree cases pass on the refactor", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 1 to 3", "output": "2 failed, 93 deselected in 2.97s (child exit 1): AC-6 rule map identity mismatch: AGENTS.md; AC-7 broken instruction backlink: .agent/docs/fixture-new-policy.md. red-check: 1 receipt(s), 2 required test(s), 0 problem(s). Refactor: 13 passed, 82 deselected in 19.49s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-row4-governance-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/row4.ps1 (task.md row 4 Validation cell, verbatim: the governance selection into tth-gov-green.txt, the whole TEST_FILE into tth-adoption-4.txt, hermetic-check.py --asserts --eol)", "cwd": "P:/av-kit", "scope": "Green for AC-6 to AC-9 and AC-14: the backlink closure, the pin rebind and test_ac_14", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 1 to 4", "output": "16 passed, 80 deselected in 27.87s; TEST_FILE 96 passed in 61.04s (base 91 plus 5); hermetic-check: 0 problem(s), asserts equal to BASE, every EOL ok"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-row5-dispatch-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/row5.ps1 (task.md row 5 Validation cell, verbatim: dispatch-check.py --exact-baseline --exit-file tth-base-dispatch.txt.exit tth-base-dispatch.txt)", "cwd": "P:/av-kit", "scope": "Red for AC-10: row 0's dispatch receipt fails exactly the placeholder pair", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 1 to 4", "output": "dispatch receipt: Total 31 PASS 29 FAIL 2 SKIP 0; exit 1; FAIL names ['placeholder receipts dir refused', 'refusal created no placeholder dir']; dispatch-check: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-row6-dispatch-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/row6.ps1 (task.md row 6 Validation cell, verbatim, plus AGENT_MODEL_REGISTRY_HOME=P:/.agent as in row 0, D-920: dispatch-check.py --source, the suite with the user's own TEMP, the leftover check, --expect-clean, hermetic-check.py --asserts --eol)", "cwd": "P:/av-kit", "scope": "Green for AC-10: arm 2 builds its token at run time", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 1 to 6", "output": "dispatch-check --source: 7 changed line(s), all in arm 2's comment and assignments, dispatch-check: 0 problem(s); suite Total: 31 | PASS: 31 FAIL: 0 SKIP: 0, exit 0; leftover %TEMP% dispatch-tests mtime before=2026-11-14T09:21:03 after=2026-11-14T09:21:03; cli-dispatch-ph-* folders before=0 after=0; dispatch receipt: Total 31 PASS 31 FAIL 0 SKIP 0; exit 0; FAIL names []; hermetic-check: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-row7-live-probe", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/row7.ps1 (task.md row 7 Validation cell, verbatim: rtk proxy uv run python docs/execution/plans/2026-11-15-tooling-test-hermeticity/live-probe.py *> C:/Temp/av-kit/tth/tth-live-probe.txt)", "cwd": "P:/av-kit", "scope": "AC-12: the real machine registry, AGENT_MODEL_REGISTRY removed in the child", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 1 to 6", "output": "cases from BASE: 7; avkit_coordinator cursor-task cursor-grok-4.6-xhigh, claude-p claude-opus-5; avkit_builder cursor-task cursor-grok-4.6-xhigh, claude-code-agents sonnet; avkit_verifier cursor-task composer-2.5-fast, claude-code-agents sonnet; avkit_router claude-code-agents haiku: each exit 0 with expected in stdout; reviewer --author-vendor anthropic: exit 0 (gpt-6.1-sol); --author-vendor openai: exit 1 (vendor_diversity_violation); validate --overlay --check-compiled: exit 0; live-probe: ok"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-row8-registers", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/row8.ps1 (task.md row 8 Validation cell, verbatim: issue-resolve.py with issue-resolve-set-8.json and --expect-sha256, issue_triage.py render, render --check, hermetic-check.py --eol)", "cwd": "P:/av-kit", "scope": "AC-13: the three issues through the repo tools", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 1 to 8", "output": "decision logs read: 95 of 95; register sha256 before=e451e517aa142eb0d03d67c1dfdddd00aa91f07df4551f124098c0de0fdedce6 after=5f1afd78bd0a1d51523cdfcc33af97d28bb197fdc9388f9ef51f0f41578117f9 CRLF=0; parsed fields changed: 13, all under status, verification and resolution_path of issues 2, 18 and 133; issue-resolve: 0 problem(s); OK: known-issues.md is up-to-date; hermetic-check: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-h1-1-unchecked", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/h1-1.ps1 (task.md row H1-1 Validation cell, verbatim)", "cwd": "P:/av-kit", "scope": "H1-1: no implementation row of task.md is unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 1 to 8", "output": "unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-gate-h1-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/h1-2-r2.ps1 (task.md row H1-2 Validation cell, verbatim, writing C:/Temp/av-kit/tth/tth-gate-h1-r2.txt: $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-tooling-test-hermeticity/session-gate.ps1 *> C:/Temp/av-kit/tth/tth-gate-h1-r2.txt; $code=$LASTEXITCODE; Select-String ... ; exit $code)", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 8, run again after Session 75's commit moved HEAD to 661d142: identity, every static check, the adoption tests and their count, the HOSTILE run, the dispatch suite with the user's TEMP and its clean check, the full Python suite, the state and issue renders, the closeout validator's selftest and the live probe, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "661d1429a026d39d9a2faacc90fb7ff1ffb95d98+df4a25e38f2ecd61dec45205a004ce89ce05c406001277e08525ccdd77bae735", "output": "identity-before exit=0, tested_state 661d1429a026d39d9a2faacc90fb7ff1ffb95d98+df4a25e38f2ecd61dec45205a004ce89ce05c406001277e08525ccdd77bae735; tools-lint exit=0 All checks passed!; py-lint exit=0 All checks passed!; task-contract exit=0 OK: 25 row(s), 23 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths exit=0 scope-check: ok; fixture-check exit=0 fixture-check: 0 problem(s); hermetic-check exit=0 hermetic-check: 0 problem(s); dispatch-source exit=0 dispatch-check: 0 problem(s); red-check-selftest exit=0 37 fixture(s) (12 positive, 25 negative), 0 wrong; adoption-tests exit=0 96 passed in 66.92s; adoption-check exit=0 adoption receipt {'passed': 96}; base {'passed': 91}; want passed 96; adoption-hostile exit=0 17 passed, 79 deselected in 3.70s; dispatch-tests exit=0 Total: 31 | PASS: 31 FAIL: 0 SKIP: 0, leftover %TEMP% dispatch-tests mtime before=2026-11-14T09:21:03 after=2026-11-14T09:21:03, cli-dispatch-ph-* folders before=0 after=0; dispatch-clean exit=0 Total 31 PASS 31 FAIL 0 SKIP 0; exit 0; FAIL names []; py-tests exit=0 2945 passed, 37 warnings in 241.04s; state-render exit=0 Drift check passed, SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content; issues-render exit=0 OK: known-issues.md is up-to-date; closeout-selftest exit=0 RESULT: 231 arm(s), 0 failure(s) [96 must-OK arms]; live-probe exit=0 live-probe: ok; identity-after exit=0 tested_state before=661d1429a026d39d9a2faacc90fb7ff1ffb95d98+df4a25e38f2ecd61dec45205a004ce89ce05c406001277e08525ccdd77bae735 after=661d1429a026d39d9a2faacc90fb7ff1ffb95d98+df4a25e38f2ecd61dec45205a004ce89ce05c406001277e08525ccdd77bae735; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-h1-3-render", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/h1-3.ps1 (task.md row H1-3 Validation cell, verbatim: rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/tth/tth-render-check.txt)", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions after this session's current-focus entry. No MEU status changes in this session", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "661d1429a026d39d9a2faacc90fb7ff1ffb95d98+df4a25e38f2ecd61dec45205a004ce89ce05c406001277e08525ccdd77bae735", "output": "Drift check passed, SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "tth-h1-4-openapi", "command": "pwsh -NoProfile -File C:/Temp/av-kit/tth/h1-4.ps1 (task.md row H1-4 Validation cell, verbatim)", "cwd": "P:/av-kit", "scope": "H1-4: the basis for skipping the OpenAPI check (packages/api content against row 0's baseline-api.json)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "661d1429a026d39d9a2faacc90fb7ff1ffb95d98+df4a25e38f2ecd61dec45205a004ce89ce05c406001277e08525ccdd77bae735", "output": "subtree packages/api: 29 files now, 29 at row 0; scope-check: ok"}
```

### Quality Gate Results

`tth-gate-h1-2` is the fresh full record, from the run after the `HEAD` move (`tth-gate-h1-r2.txt`). Its last line is:

> session-gate: all steps exit 0

| Step | Stage | Exit | Result |
|------|-------|------|--------|
| identity-before | identity | 0 | `tested_state` recorded |
| tools-lint | static | 0 | `All checks passed!` |
| py-lint | static | 0 | `All checks passed!` |
| task-contract | static | 0 | 25 rows, 23 fully checked, 2 exempt (`view_file`: H1-5, H2-1) |
| scope-paths | static | 0 | `scope-check: ok` |
| fixture-check | static | 0 | `fixture-check: 0 problem(s)` |
| hermetic-check | static | 0 | `hermetic-check: 0 problem(s)`, every EOL rule ok |
| dispatch-source | static | 0 | `dispatch-check: 0 problem(s)` |
| red-check-selftest | static | 0 | 37 fixtures (12 positive, 25 negative), 0 wrong |
| adoption-tests | targeted | 0 | `96 passed in 66.92s` |
| adoption-check | targeted | 0 | passed 96 = base 91 + 5 |
| adoption-hostile | targeted | 0 | `17 passed, 79 deselected in 3.70s` under `HOSTILE` |
| dispatch-tests | targeted | 0 | Total 31, PASS 31, FAIL 0; leftover folder mtime unchanged; `cli-dispatch-ph-*` 0 before and after |
| dispatch-clean | targeted | 0 | `Total 31 PASS 31 FAIL 0 SKIP 0; exit 0; FAIL names []` |
| py-tests | full | 0 | `2945 passed, 37 warnings in 241.04s` (row 0: 2940; +5 new tests) |
| state-render | full | 0 | Drift check passed (153 MEUs, 12 phases) |
| issues-render | full | 0 | `OK: known-issues.md is up-to-date` |
| closeout-selftest | full | 0 | 231 arms, 0 failures (96 must-OK) |
| live-probe | full | 0 | `live-probe: ok` |
| identity-after | identity | 0 | `tested_state` equal before and after |

`tested_state` `661d1429a026d39d9a2faacc90fb7ff1ffb95d98+df4a25e3…d77bae735`, the same before and after the gate, and re-derived the same by `identity.py --state-only` after H1-3 and H1-4 ran again (their outputs are `PROJECT_ARTIFACTS`).

The first run, on `3397e78d7342d73e99dde3b43244a55cd6be7e87+7763c700…cabecaa8` before the `HEAD` move, also ended `session-gate: all steps exit 0` (`tth-gate-h1.txt`, step receipts under `gate-r1/`; adoption 96 in 65.12s, HOSTILE 17 in 13.13s, pytest 2945 in 254.61s). The gate ran a second time only because `HEAD` moved; no step failed in either run.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `tests/tooling/test_framework_adoption.py` | modified | The registry home, `fixture_wrapper`, the five rewired tests and AC-2 (rows 1 and 2); `build_migrated_tree`, the closure and rebind helpers, `tracked_pin_mismatches`, AC-6, AC-7, AC-8 and AC-14 (rows 3 and 4). CRLF on every line, no BOM, kept; 1,072 to 1,275 lines, 40,489 to 49,718 bytes |
| `tests/tooling/fixtures/registry-home/model-registry.json` | new | The synthetic registry; LF, 197 lines, 3,804 bytes |
| `tests/tooling/fixtures/registry-home/make_fixture.py` | new | Its generator; LF, standard library only, 178 lines |
| `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1` | modified | Arm 2's comment and three assignments (7 changed lines at `:557-571`); UTF-8 BOM and CRLF kept; 1,133 to 1,135 lines |
| `.agent/context/known-issues.yaml` | modified, by `issue-resolve.py` only | The three issues' `status`, `verification` and `resolution_path`; LF kept |
| `.agent/context/known-issues.md` | regenerated, by `issue_triage.py render` only | Their rows; LF kept |
| `.agent/context/current-focus.md` | modified | This session's entry on top (H1-3); CRLF kept, the rest of the file unchanged |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-blobs.json`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-api.json`, `red-require.txt`, `red-check.py` (D-919), `identity.py`, `scope-check.py`, `issue-resolve.py`, `fixture-check.py`, `hermetic-check.py`, `dispatch-check.py`, `live-probe.py`, `session-gate.ps1` (new in H1-2), `task.md` (rows marked) | new or modified | The plan's records, oracles and gate |

`known-issues.yaml`, `known-issues.md` and `current-focus.md` were already dirty at row 0 from Session 75. Session 75's commit `661d142` holds them at their row-0 bytes, so `git diff HEAD` now shows only this session's changes: in the register, exactly the 13 parsed fields that `issue-resolve.py` reports.

```diff
-            # 2. An uninstantiated placeholder. Rooted under the real temp dir on
-            #    purpose: creating it would genuinely SUCCEED, so this arm proves the
-            #    guard fired rather than that the OS happened to reject the path.
+            # 2. An uninstantiated placeholder. The token is assembled at run time from
+            #    braces and its name, because instantiation rewrites any literal token in
+            #    this file. The path sits in a fresh folder under the real temp folder, so
+            #    creating it would genuinely SUCCEED: a pass proves the guard fired.
 ...
-            $phBase = Join-Path ([System.IO.Path]::GetTempPath()) 'av-kit'
-            $env:RECEIPTS_DIR = Join-Path $phBase 'receipts'
+            $phToken = ('{' * 2) + 'PROJECT_NAME' + ('}' * 2)
+            $phBase = Join-Path ([System.IO.Path]::GetTempPath()) ('cli-dispatch-ph-' + [guid]::NewGuid().ToString('N'))
+            $env:RECEIPTS_DIR = Join-Path (Join-Path $phBase $phToken) 'receipts'
```

```diff
-def test_registry_contract_preserves_bindings(class_name, harness, expected):
+def test_registry_contract_preserves_bindings(class_name, harness, expected, registry_home):
     result = run(
-        Path("P:/.agent/tools/resolve_model.py"),
+        registry_home["resolver"],
 ...
         "--project",
-        ROOT,
+        registry_home["project"],
 ...
-        env={"AGENT_MODEL_REGISTRY_HOME": "P:/.agent"},
+        env=registry_home["env"],
```

The same input-only change applies to `test_registry_contract_vendor_independence`, `test_registry_contract_unsupported_harness_refused` and `test_registry_contract_bad_configuration_refused`. The wrapper test's change:

```diff
-    env = os.environ | {"RECEIPTS_DIR": "C:/Temp/av-kit", "AGENT_MODEL_REGISTRY_HOME": "P:/.agent"}
+    env = os.environ | {"RECEIPTS_DIR": "C:/Temp/av-kit"} | registry_home["env"]
 ...
-            str(ROOT / "tools/Invoke-CodexDispatch.ps1"),
+            str(fixture_wrapper(tmp_path / "wrapper", registry_home["project"])),
```

```diff
         elif source.is_file():
             target.parent.mkdir(parents=True, exist_ok=True)
             shutil.copyfile(source, target)
+    copy_backlink_targets(root, overrides)
+    rebind_instruction_pins(root)
     sources: dict[str, bytes] = {}
```

```diff
+def test_ac_14_tracked_rule_map_pin_matches_live_instructions(tmp_path):
+    mismatches = tracked_pin_mismatches(ROOT)
+    assert mismatches == [], "\n".join(mismatches)
+    (tmp_path / RULE_MAP).parent.mkdir(parents=True)
+    shutil.copyfile(ROOT / RULE_MAP, tmp_path / RULE_MAP)
+    (tmp_path / "AGENTS.md").write_bytes((ROOT / "AGENTS.md").read_bytes() + b"\n")
+    shutil.copyfile(ROOT / "GUARDRAILS.md", tmp_path / "GUARDRAILS.md")
+    mismatches = tracked_pin_mismatches(tmp_path)
+    assert len(mismatches) == 1, mismatches
+    assert "AGENTS.md" in mismatches[0] and "p.write_bytes(" in mismatches[0], mismatches
```

Line endings and BOM, measured as Python bytes after the last edit: `TEST_FILE` 1,275 CRLF of 1,275 lines, no BOM; `DISPATCH_TEST` BOM, 1,135 CRLF of 1,135 lines; `FIXTURE`, `make_fixture.py`, `known-issues.yaml` (5,280 lines) and `known-issues.md` (62 lines) 0 CR; `session-gate.ps1` LF, no BOM. `hermetic-check.py --eol` passed after every editing row and in the gate.

---

## Codex Validation Report

Left for the reviewer. The H1-7 execution review writes the verdict to `.agent/context/handoffs/2026-11-15-tooling-test-hermeticity-implementation-critical-review.md`; this section only records it.

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

The H1-7 review, round 1 of loop `tth-execution-2026-11-15-tooling-test-hermeticity` (cap 6), raised no finding.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Verdict

**approved** at round 1 of 6: 0 findings, 0 blocking, intent achieved: yes. Usage 6,715,571 tokens.

- The review answered Q1 to Q6 (all accepted), found no weak test in its IR-5 audit, and marked IR-1, IR-4 to IR-7, DR, D-919 and D-920 `pass`, with IR-2 and IR-3 `n/a`.
- The reviewer's `tested_state` was `3397e78d7342d73e99dde3b43244a55cd6be7e87+7763c700…cabecaa8`, equal to the gate's at that time and measured before Session 75's commit moved `HEAD` (see the Execution notes).
- H1-7a, the review-state check: `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`.
- H1-7b, the execution-review check: `OK: approved at round 1 of 6, 0 open blocking findings`.
- The canonical review is `.agent/context/handoffs/2026-11-15-tooling-test-hermeticity-implementation-critical-review.md`, a byte copy of the reviewer's output.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `TOOLING-SHARED-REGISTRY-COUPLING`'s residual: a machine registry bump still reds `tests/tooling/test_hdp_expert_pass.py::test_ac_10_compiled_registry_is_current_and_adds_only_the_peer_reviewer` until the overlay is revalidated | residual, by design | — | D-912: the red is a true signal, because the wrapper refuses the same stale stamp at every real dispatch; the issue is `mitigated` |
| Upstream's latent placeholder defect | out-of-scope | Mat | D-913: `P:/agentic-framework` is not edited |
| The empty leftover folder in the temp folder | out-of-scope | Mat | D-914: only Mat removes it |
| Commit and push | out-of-scope | Mat | The commit runs only on Mat's direction; Session 75 is uncommitted in the same tree |

**Notes for Mat.**

- **Upstream's latent defect (D-913).** `P:/agentic-framework`'s `core/.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1` still writes the literal `{{PROJECT_NAME}}` token in arm 2 (its line 619). Any project instantiated from it gets the same two failing checks av-kit had, because instantiation replaces the token. av-kit's copy now diverges from upstream there on purpose. The fix to carry upstream is this session's three assignment lines and comment.
- **The leftover folder (D-914).** An earlier run of the old arm left an empty folder under the temp folder. After you check that both are empty, remove it and then its empty parent:
  `Remove-Item -LiteralPath (Join-Path $env:TEMP 'av-kit/receipts/dispatch-tests')`, then `Remove-Item -LiteralPath (Join-Path $env:TEMP 'av-kit/receipts')`.
  This session did not touch it: its mtime is `2026-11-14T09:21:03` before and after every dispatch run.
- **New upkeep (D-911).** When the project overlay `.agent/model-registry.local.yaml` is rebound, also re-run `uv run python tests/tooling/fixtures/registry-home/make_fixture.py`, so the fixture keeps every slug the overlay names. `fixture-check.py` and `test_ac_2_…` fail loudly if it does not.
- **After an `AGENTS.md` or `GUARDRAILS.md` edit (D-915, M-6).** `test_ac_14_tracked_rule_map_pin_matches_live_instructions` is now the one red, not four tests. Its message names the file, the old pin and the new hash, says to check that the rule map still covers the edited blocks, and gives the one-line `uv run python -c "…"` rebind command. Commit the rebind alone, as D-132 rules.
- **`current-focus.md` is shared.** Session 76's entry sits above Session 75's.

---

## Decision Log

```yaml
decision_log:
  - id: D-919
    stage: execution
    question: "Row 1's red-check reported required tests as missing: pytest pads a long test id's failure header with fewer than three underscores, and the copied PYTEST_HEADER pattern needs three. How does red-check read those headers?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "PYTEST_HEADER becomes ^_+ (.+?) _+\\s*$ in this plan's red-check.py, and its selftest gains a long-id fixture (37 fixtures, 0 wrong); no other logic changes"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-tooling-test-hermeticity/red-check.py:82 — the new pattern", "docs/execution/plans/2026-11-15-framework-small-syncs/red-check.py:80 — the peer's ^_{3,} pattern", "docs/execution/plans/2026-11-15-tooling-test-hermeticity/implementation-plan.md:354 — red-check.py is used unchanged in logic"]
    research: { engine: local-measurement, sources: ["tth-reg-red.txt lines 11-53: seven headers of the form _ test_registry_contract_preserves_bindings[...] _"] }
    reasoning: "The receipt shows the headers pytest really writes, so the pattern was wrong for this suite's long parametrized ids, not the Red. Widening the underscore run reads the same blocks the plan meant red-check to read, and the selftest keeps every earlier refusal (25 negatives, 0 wrong). Passing the row by hand lost, because the plan makes red-check the proof that each required test failed by assertion. The change is local to this plan's copy and two-way."
  - id: D-920
    stage: execution
    question: "Row 6's first suite run exited 1 with registry_not_found, because the row command does not set AGENT_MODEL_REGISTRY_HOME, which row 0's baseline.ps1 sets for the same suite. How does row 6 run?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 6's wrapper sets AGENT_MODEL_REGISTRY_HOME=P:/.agent, as row 0 and the gate do; the failed run's receipts are kept under -noregistry names and disclosed"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-tooling-test-hermeticity/baseline.ps1:26 — row 0 sets AGENT_MODEL_REGISTRY_HOME=P:/.agent for the base dispatch run", "docs/execution/plans/2026-11-15-tooling-test-hermeticity/session-gate.ps1 — the gate sets the same variable", "codex-dispatch registry home: Invoke-CodexDispatch exits registry_not_found without it"]
    research: { engine: local-measurement, sources: ["tth-dispatch-green-noregistry.txt: registry_not_found: no ModelRegistry.psm1 at any S2 location"] }
    reasoning: "Row 5's Red is row 0's receipt, so the Green must run the suite in row 0's environment to compare like with like. The variable only tells the wrapper where the machine module is; it is not the HOSTILE variable and changes no assertion. The failed run created no placeholder folder and left the leftover folder as it was. Changing the task row's text lost, because the plan was approved and the wrapper change is enough."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-15 | claude-code-local (Claude Opus 5.5) | Initial handoff after H1-2, H1-3 and H1-4; for the H1-7 execution review |
| Updated | 2026-11-15 | claude-code-local (Claude Opus 5.5) | The H1-7 Codex report (approved at round 1 of 6), the `HEAD` move to `661d142`, and the H1-2 gate run on the new state |
