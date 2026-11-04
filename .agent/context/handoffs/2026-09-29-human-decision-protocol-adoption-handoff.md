---
date: "2026-09-29"
project: "2026-09-29-human-decision-protocol-adoption"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-29-human-decision-protocol-adoption/implementation-plan.md"
build_plan_section: "none (governance; meus: [])"
agent: "claude-code-main-session"
reviewer: "claude-fable-5-1-subagent"
predecessor: "2026-09-26-framework-update-adoption-handoff.md"
---

# Handoff: 2026-09-29-human-decision-protocol-adoption-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. This is governance work: it adopts upstream `matbanik/agentic-framework@4033418f66d2d2085f989e27bf2823d9c55332b6`.
**Build Plan Section**: none
**Predecessor**: [2026-09-26-framework-update-adoption-handoff.md](2026-09-26-framework-update-adoption-handoff.md)

Implementation commit: `f34e8a98549e09a9745d096ddf44cfa8d3f03a67` on `claude/nice-mayer-dl4n8u`. Plan, task and evidence:
`docs/execution/plans/2026-09-29-human-decision-protocol-adoption/`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | unit | Protocol doc installed with no unfilled tokens; AGENTS, commands.md and harness-profiles route to it | Spec | row 2 token check; `AGENTS.md:27`; `.agent/docs/commands.md` protocol row; `harness-profiles.md` `web_search_tool` row | ✅ |
| AC-2 | unit | Every upstream hunk is present, applied or hand-merged, as recorded in the plan's scope table | Spec | per-file `patch` application log (plan §Scope) | ✅ |
| AC-3 | unit | Closeout validator selftest reports 174 / 0 / 45 on Python 3.11 | Spec + Local Canon | `closeout-selftest` | ✅ |
| AC-4 | unit | Linter and ledger selftests still pass | Local Canon | `lint-selftest`, `ledger-selftest` | ✅ |
| AC-5 | unit | Ruff and Pyright are clean on changed Python | Local Canon | `pyright-changed`, `ruff-validator` | ✅ |
| AC-6 | integration | `tests/tooling` failure set is unchanged from baseline | Local Canon | `tooling-suite` | ✅ |
| AC-7 | unit | AGENTS.md stays within 20,000 bytes / 170 lines with no net rule growth | Local Canon | `wc -c AGENTS.md` = 17063 bytes, 124 lines | ✅ |
| AC-8 | unit | Twin templates are byte-identical to `.agent/templates/*` | Local Canon | `cmp` of each pair: identical | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| validator import on 3.11 | `SyntaxError: f-string expression part cannot include a backslash` (unmodified upstream line) | selftest 174/0 | `tools/validate_closeout_artifacts.py:1132-1135` (`yaml_sequence`, `indent` hoisted out of the f-string) |
| validator `os` import | `NameError: name 'os' is not defined` in `path_matches_declared` | selftest 174/0 | `tools/validate_closeout_artifacts.py:40` |
| `shipped-handoff-template-present` arm | `FAIL … got=template file missing` | 3 shipped-template arms ok | `tools/validate_closeout_artifacts.py` (shipped_handoff_template path) |
| pyright on validator | 4 errors: `fenced_plan` bound as str and as nested function | 0 errors | rename to `fenced_heading_plan` |
| repeated-ID arms (Round 1 Finding 1) | `177 arm(s), 3 failure(s)`: `handoff-decision-log-repeated-id-refused`, `plan-repeated-id-across-fences-refused`, `grouping-repeated-id-refused` each got `0/OK`, wanted `1/REFUSE` | `177 arm(s), 0 failure(s)` | `tools/validate_closeout_artifacts.py` `refuse_repeated_ids`, called from `decision_entries` and `decision_sources` |

### Commands Executed

Fresh on commit `2affab69c3d8e7dfbf9e3acd2b9e428647af6861` (Round 1 corrections), Linux container, Python 3.11.15, `R=/tmp/claude-0/r`. `rtk` and
`pwsh` are absent here, so POSIX redirects were used. The Windows receipt forms are in `task.md`.

```json
{"schema_version": "evidence.v1", "check_id": "closeout-selftest", "command": "uv run --no-sync python tools/validate_closeout_artifacts.py --selftest > $R/st.txt 2>&1; echo $?", "cwd": "/home/user/av-kit", "scope": "closeout validator, all arms, Python 3.11.15", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "2affab69c3d8e7dfbf9e3acd2b9e428647af6861", "output": "RESULT: 177 arm(s), 0 failure(s) [45 must-OK arms, so the tool is not refusing everything]", "fresh": true}
```
```json
{"schema_version": "evidence.v1", "check_id": "lint-selftest", "command": "uv run --no-sync python tools/lint_task_contract.py --selftest > $R/l.txt 2>&1; echo $?", "cwd": "/home/user/av-kit", "scope": "task-contract linter arms", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "2affab69c3d8e7dfbf9e3acd2b9e428647af6861", "output": "RESULT: 50 arm(s), 0 failure(s) [14 must-OK arms, so the linter is not refusing everything]", "fresh": true}
```
```json
{"schema_version": "evidence.v1", "check_id": "ledger-selftest", "command": "RECEIPTS_DIR=$R uv run --no-sync python tools/review_ledger.py selftest > $R/lg.txt 2>&1; echo $?", "cwd": "/home/user/av-kit", "scope": "review ledger arms", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "2affab69c3d8e7dfbf9e3acd2b9e428647af6861", "output": "RESULT: 105 arm(s), 0 failure(s) [53 must-OK arms, so the tool is not refusing everything]", "fresh": true}
```
```json
{"schema_version": "evidence.v1", "check_id": "pyright-changed", "command": "uv run --no-sync pyright tools/validate_closeout_artifacts.py tools/issue_triage/model.py > $R/py.txt 2>&1; echo $?", "cwd": "/home/user/av-kit", "scope": "changed Python files", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "2affab69c3d8e7dfbf9e3acd2b9e428647af6861", "output": "0 errors, 0 warnings, 0 informations", "fresh": true}
```
```json
{"schema_version": "evidence.v1", "check_id": "ruff-changed", "command": "uv run --no-sync ruff check tools/validate_closeout_artifacts.py tools/issue_triage/model.py && uv run --no-sync ruff format --check tools/validate_closeout_artifacts.py tools/issue_triage/model.py", "cwd": "/home/user/av-kit", "scope": "changed Python files", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "2affab69c3d8e7dfbf9e3acd2b9e428647af6861", "output": "All checks passed! / 2 files already formatted", "fresh": true}
```
```json
{"schema_version": "evidence.v1", "check_id": "known-issues-model", "command": "uv run --no-sync python -c \"...model.validate(yaml.safe_load(open('.agent/context/known-issues.yaml')))...\"", "cwd": "/home/user/av-kit", "scope": "known-issues.yaml against the updated issue_triage model", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "2affab69c3d8e7dfbf9e3acd2b9e428647af6861", "output": "errors []", "fresh": true}
```
```json
{"schema_version": "evidence.v1", "check_id": "repeat-id-probe", "command": "sed 's/  - id: D-4/  - id: D-3/' <this handoff> > $R/p11/x-handoff.md; uv run --no-sync python tools/validate_closeout_artifacts.py --handoff $R/p11/x-handoff.md --handoff-structure-only", "cwd": "/home/user/av-kit", "scope": "Round 1 reviewer probe P11 (this handoff with D-4 relabelled D-3)", "phase": "targeted", "exit_code": 1, "result": "fail", "tested_state": "2affab69c3d8e7dfbf9e3acd2b9e428647af6861", "output": "REFUSE: handoff … Decision Log decision_log repeats decision ID D-3; each decision needs its own ID, or the second record cannot be matched to a reflection row (human-decision-protocol.md §6). Expected refusal: before the fix this probe passed with '5 decision(s) logged'.", "fresh": true}
```
```json
{"schema_version": "evidence.v1", "check_id": "tooling-suite", "command": "uv run --no-sync pytest tests/tooling -q -p no:cacheprovider > $R/tt2.txt 2>&1; echo $?", "cwd": "/home/user/av-kit", "scope": "tests/tooling (Linux container; needs P:/ paths and pwsh for 32 cases)", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "2affab69c3d8e7dfbf9e3acd2b9e428647af6861", "output": "32 failed, 59 passed. The sorted FAILED-ID list is identical to the baseline at f34e8a9~1 (32 failed, 59 passed; diff empty). Causes: P:/agentic-framework, P:/.agent/tools/resolve_model.py, pwsh absent.", "fresh": true}
```
### Quality Gate Results

```
pyright: 0 errors, 0 warnings (changed files)
ruff: 0 violations, both changed files formatted
pytest tests/tooling: 59 passed, 32 failed (the baseline failure set, identical by ID)
selftests: closeout 177/0 (45 must-OK), linter 50/0, ledger 105/0
anti-placeholder: no unfilled template tokens in the protocol doc
```

Product suites (Vitest, Electron, pytest unit/integration, OpenAPI) were not run. This change
touches no product code or product configuration.

---

## Changed Files

36 files in `f34e8a98549e09a9745d096ddf44cfa8d3f03a67` (+4046 / −141). The full per-file table is in the plan's §Scope. Key deltas:

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `.agent/docs/human-decision-protocol.md` | new | 1–283 | Upstream protocol; ADR row adapted to av-kit (plan D-2) |
| `AGENTS.md` | modified | 27 | Existing gap-resolution rule extended to route through the protocol (plan D-1) |
| `tools/validate_closeout_artifacts.py` | modified | +~2300 | Upstream Decisions Log reconciliation; handoff requires `## Decision Log`; local fixes D-3/D-4/D-8 |
| `tools/issue_triage/model.py` | modified | 284–299 | `enrichment.decision_log` must be a list of mappings |
| `.agent/skills/cli-dispatch/SKILL.md` | modified | §3 Fallback steps | Rate-limit stop presented as a Decision Brief (Mat vs timed retry; plan D-5) |
| templates + twins | modified | — | Decision Log sections; TASK H2-2 `--decision-source` flags |

```diff
-    pattern = rf"^{'' if root else '(?P<indent>[ \t]*)'}{spelled}:(?P<rest>[^\n]*)$"
+    indent = "" if root else r"(?P<indent>[ \t]*)"
+    pattern = rf"^{indent}{spelled}:(?P<rest>[^\n]*)$"
```

```diff
-    shipped_handoff_template = Path(__file__).resolve().parents[1] / "templates" / "HANDOFF-TEMPLATE.md"
+    shipped_handoff_template = (
+        Path(__file__).resolve().parents[1] / ".agent" / "context" / "handoffs" / "TEMPLATE.md"
+    )
```

---

## Codex Validation Report

_Left blank for reviewer agent. The rolling review file is canonical:_
`.agent/context/handoffs/2026-09-29-human-decision-protocol-adoption-implementation-critical-review.md`.

---

## Corrections Applied (2026-09-29)

Round 1 (`approved`, four non-blocking findings) was followed by the user's direction to address
them. Corrections are in `2affab6`; the plan, task and this handoff were updated after it.

**Findings resolved**: 4/4, plus 3 of the 4 out-of-contract observations

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| 1 | Repeated decision ID within one source was dropped silently | New `refuse_repeated_ids`, called at the end of `decision_entries` (each fenced block, the handoff section, the issue log, a YAML source) and per source in `decision_sources` (a plan's fences taken together, a grouping's §8 rows). Across sources, one ID with one stage is still allowed, as upstream allows. Recorded as D-9 | 3 new arms Red → Green (see FAIL_TO_PASS); `repeat-id-probe` |
| 2 | Restated "6 `##` + 9 `###`" count at `completion-preflight/SKILL.md:101` contradicts D-7 | Replaced with "every `##` and `###` heading, incl. `### Decisions Log`" | `grep` finds no heading count in the skill |
| 3 | AC-5 claimed ruff-clean while `model.py:228` had a pre-existing E501 | Wrapped the line and ruff-formatted the file (format-only, 7+/15−) | `ruff-changed` |
| 4 | Task row 7 command lacked `--max-review-rounds` | Added `--max-review-rounds 6` | Round 1 reviewer ran it: exit 0 |
| O1 | Stale "9 sections" at `development-lifecycle.md:430` | Replaced with "every template heading, incl. `### Decisions Log` (H2-2 validator)" | read back |
| O2 | `context-compression.md` variable-content list lacked the Decision Log | Added `Decision Log` | read back |
| O3 | Task row 1 said 31 files | Now "36 files in `f34e8a9`" | `git show --stat f34e8a9` |
| O4 | `harness.local.md` does not record `web_search_tool` | Not changed. `harness-profiles.md:94` says the flag is resolved from the active tool surface once per session; a pinned value would contradict that rule, and `harness.local.md` is a human-confirmed override file | — |

---

## Deferred Items

None.

---

## Decision Log

<!-- Every .agent/docs/human-decision-protocol.md decision made during this MEU, autonomous or human-ruled, as ONE fenced decision_log: YAML block with the plan's entry shape, or exactly `None.` (delete the example below in that case). This comment may stay; any other prose here is refused. The closeout validator reconciles every entry with the reflection's Decisions Log; an example left unfilled is refused, not ignored. -->

```yaml
decision_log:
  - id: D-3
    stage: execution
    question: "The upstream validator uses a backslash inside an f-string replacement field (Python 3.12+ only). Keep it or rewrite it?"
    resolution: autonomous
    class: two-way
    chosen: "Rewrite with the regex fragment hoisted out of the f-string"
    source_tag: Local Canon
    precedents: ["pyproject.toml:5 — requires-python >=3.11; [tool.ruff] target-version py311"]
    research: { engine: none, sources: ["unavailable — the language rule is a documented Python 3.12 change (PEP 701)"] }
    reasoning: "Under 3.11 the file does not import, so every closeout gate would fail. The rewrite builds the same pattern. The alternative, raising the floor to 3.12, is a product-wide change that does not belong in a governance adoption."
  - id: D-4
    stage: execution
    question: "The selftest arm that reads the shipped handoff template looks for templates/HANDOFF-TEMPLATE.md. Which local file should it read?"
    resolution: autonomous
    class: two-way
    chosen: ".agent/context/handoffs/TEMPLATE.md"
    source_tag: Local Canon
    precedents: [".agent/docs/artifact-naming.md:18 — Template: .agent/context/handoffs/TEMPLATE.md"]
    research: { engine: none, sources: ["unavailable — repository layout question"] }
    reasoning: "That is the canonical handoff template agents read. Without the change the arm reports 'template file missing' and the selftest fails."
  - id: D-6
    stage: execution
    question: "The four templates have twin copies. Update the twins too?"
    resolution: autonomous
    class: two-way
    chosen: "Re-sync each twin from .agent/templates/"
    source_tag: Local Canon
    precedents: ["artifact-naming.md:18,29 — the twins are the canonical paths agents read", "the twins were byte-identical to .agent/templates/* before this change"]
    research: { engine: none, sources: ["unavailable — repository layout question"] }
    reasoning: "Workflows read the twins, so updating only .agent/templates/ would leave agents on the old shape. The validator would then refuse handoffs that lack the new ## Decision Log section."
  - id: D-7
    stage: execution
    question: "completion-preflight: adopt upstream's '6 ## + 9 ###' heading count?"
    resolution: autonomous
    class: two-way
    chosen: "Say 'every template heading' without a count"
    source_tag: Local Canon
    precedents: [".agent/skills/completion-preflight/SKILL.md:163 — the local text already said '7 sections' where upstream said '11'"]
    research: { engine: none, sources: ["unavailable — wording choice"] }
    reasoning: "A count restated in prose drifted once already. The validator enforces the real template, so naming the rule without a number cannot go stale."
  - id: D-8
    stage: execution
    question: "The upstream validator fails local Ruff (format, E501, UP035) and Pyright (fenced_plan bound as both str and function). Fix it locally?"
    resolution: autonomous
    class: two-way
    chosen: "Apply ruff format, wrap three long lines, noqa one verbatim template-mirror string, import Iterator from collections.abc, and rename the str binding to fenced_heading_plan"
    source_tag: Local Canon
    precedents: ["AGENTS.md §Code Quality", "pyproject.toml [tool.ruff] line-length 100", "d6cd5a3 — the previous adoption left this file ruff-formatted"]
    research: { engine: none, sources: ["unavailable — tool configuration"] }
    reasoning: "The changes affect style and names only. The selftest result (174/0/45) is identical before and after them."
  - id: D-9
    stage: execution
    question: "Fix Round 1 Finding 1 (repeated decision ID dropped silently) in this change, or defer it?"
    resolution: human
    class: two-way
    chosen: "Fix in this change: refuse a repeated ID within one source, with three selftest arms"
    source_tag: Human-approved
    precedents: [".agent/context/handoffs/2026-09-29-human-decision-protocol-adoption-implementation-critical-review.md Finding 1 — recommended a local selftest arm and an upstream issue"]
    research: { engine: none, sources: ["unavailable — the defect was reproduced locally; no external question"] }
    reasoning: "The reflection side already refuses duplicate rows, so refusing them on the source side makes both sides consistent. The check only refuses input that was previously lost silently. Deferring would leave the new closeout gate able to lose a decision."
    human_message_reference: "USER_EXPLICIT 2026-09-29 'address the findings if you already have not done so'"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-29 | claude-code-main-session | Initial handoff |
| Submitted for review | 2026-09-29 | claude-code-main-session | Sent to a Fable 5.1 subagent per `human-review-decision.md` |
| Review complete | 2026-09-29 | claude-fable-5-1-subagent | Round 1 verdict: approved (4 non-blocking findings) |
| Corrections applied | 2026-09-29 | claude-code-main-session | 4/4 findings and 3 observations resolved in `2affab6`; sent to Round 2 |
