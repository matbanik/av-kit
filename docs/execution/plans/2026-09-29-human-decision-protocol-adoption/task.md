---
project: "2026-09-29-human-decision-protocol-adoption"
source: "docs/execution/plans/2026-09-29-human-decision-protocol-adoption/implementation-plan.md"
meus: []
status: "in_progress"
template_version: "2.2"
---

# Task — Adopt the framework's Human Decision Protocol

> **Project:** `2026-09-29-human-decision-protocol-adoption`
> **Type:** Infrastructure/Docs (governance; no product surface)

User direction (trusted chat, 2026-09-29): "adopt the human decision protocol from this repo that
was just added: https://github.com/matbanik/agentic-framework". Source pinned at
`4033418f66d2d2085f989e27bf2823d9c55332b6`.

This session ran in a Linux cloud container with Python 3.11.15. `pwsh` and `rtk` are not
installed there, so the evidence below was captured with POSIX redirects (`> file 2>&1; echo $?`).
The Validation cells give the canonical Windows receipt commands for re-running on the dev
machine.

## Task Table

| # | Task | Owner | Deliverable | Validation | Depends on | Context strategy | Durable outputs | builder_model | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Apply the upstream per-file diffs (tokens instantiated) and hand-merge the rejected hunks | coder | 36 files in `f34e8a9` | `rtk proxy git diff --stat *> C:/Temp/av-kit/hdp-diffstat.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/hdp-diffstat.txt; exit $code` | — | shared | Diff in this commit | `avkit_coordinator` | `[x]` |
| 2 | Install `human-decision-protocol.md` with local adaptations | coder | `.agent/docs/human-decision-protocol.md` | `rtk proxy uv run python -c "import pathlib,sys; t=pathlib.Path('.agent/docs/human-decision-protocol.md').read_text(encoding='utf-8'); print('unfilled tokens:', t.count(chr(123)*2)); sys.exit(t.count(chr(123)*2) > 0)" *> C:/Temp/av-kit/hdp-tokens.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/hdp-tokens.txt; exit $code` | 1 | shared | Protocol doc | `avkit_coordinator` | `[x]` |
| 3 | Validator selftest on the Python floor | tester | 177 arms / 0 failures / 45 must-OK | `rtk proxy uv run python tools/validate_closeout_artifacts.py --selftest *> C:/Temp/av-kit/hdp-selftest.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/hdp-selftest.txt; exit $code` | 1 | shared | Selftest receipt | `avkit_verifier` | `[x]` |
| 4 | Companion selftests | tester | Lint and ledger selftests pass | `rtk proxy uv run python tools/lint_task_contract.py --selftest *> C:/Temp/av-kit/hdp-lint.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/hdp-lint.txt; exit $code` | 1 | shared | Lint receipt | `avkit_verifier` | `[x]` |
| 5 | Static checks on changed Python | tester | Ruff and Pyright clean | `rtk proxy uv run pyright tools/validate_closeout_artifacts.py tools/issue_triage/model.py *> C:/Temp/av-kit/hdp-pyright.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/hdp-pyright.txt; exit $code` | 3 | shared | Pyright receipt | `avkit_verifier` | `[x]` |
| 6 | Tooling regression comparison against baseline | tester | Identical failure set | `rtk proxy uv run pytest tests/tooling -q *> C:/Temp/av-kit/hdp-tooling.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/hdp-tooling.txt; exit $code` | 3 | shared | Tooling receipt | `avkit_verifier` | `[x]` |
| 7 | Independent review of this adoption | reviewer | Approved verdict bound to this target | `rtk proxy uv run python tools/validate_closeout_artifacts.py --review .agent/context/handoffs/2026-09-29-human-decision-protocol-adoption-implementation-critical-review.md --review-state-only --max-review-rounds 6 --output C:/Temp/av-kit/hdp-review-state.json *> C:/Temp/av-kit/hdp-review.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/hdp-review.txt; exit $code` | 3, 4, 5, 6 | shared | Rolling review file | `avkit_coordinator` | `[x]` |

## Evidence

Receipts from this session (Linux, Python 3.11.15, `uv run --no-sync`):

| Check | Exit | Decisive output |
|---|---|---|
| `python tools/validate_closeout_artifacts.py --selftest` (on `f34e8a9`) | 0 | `RESULT: 174 arm(s), 0 failure(s) [45 must-OK arms, so the tool is not refusing everything]` |
| Same, after the Round 1 corrections (`2affab6`) | 0 | `RESULT: 177 arm(s), 0 failure(s) [45 must-OK arms …]` |
| Same, the 3 new repeated-ID arms before the fix | 1 | `177 arm(s), 3 failure(s)`: each arm got `0/OK` where it wanted `1/REFUSE` |
| Same, before D-3 (unmodified upstream code) | 1 | `SyntaxError: f-string expression part cannot include a backslash` (line 1119) |
| Same, before D-4 | 1 | `FAIL shipped-handoff-template-present want=0/OK got=template file missing` |
| `python tools/lint_task_contract.py --selftest` | 0 | `RESULT: 50 arm(s), 0 failure(s) [14 must-OK arms …]` |
| `RECEIPTS_DIR=… python tools/review_ledger.py selftest` | 0 | `RESULT: 105 arm(s), 0 failure(s) [53 must-OK arms …]` |
| `lint_task_contract.py --template-mode --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task .agent/templates/TASK-TEMPLATE.md` (RECEIPTS_DIR=C:/Temp/av-kit) | 0 | `OK: 18 row(s); 10-column table …; 12 row(s) fully checked` |
| `pyright tools/validate_closeout_artifacts.py tools/issue_triage/model.py` | 0 | `0 errors, 0 warnings, 0 informations` |
| `ruff check tools/validate_closeout_artifacts.py` / `ruff format --check` | 0 / 0 | `All checks passed!` / `1 file already formatted` |
| `ruff check tools/issue_triage/model.py` | 1 → 0 | The one pre-existing E501 at line 228 was wrapped and the file ruff-formatted in `2affab6` (Round 1 Finding 3) |
| `issue_triage.model.validate(known-issues.yaml)` | 0 | `errors []` |
| `pytest tests/tooling -q`, after | 1 | `32 failed, 59 passed` |
| `pytest tests/tooling -q`, baseline (`git stash -u`) | 1 | `32 failed, 59 passed`; failure-ID diff between the runs is empty. Both sets need `P:/agentic-framework`, `P:/.agent/tools/resolve_model.py` or `pwsh`, which this container lacks |
| `diff` of each twin template vs `.agent/templates/*` | 0 | Byte-identical (copied after edit) |
| `wc -c AGENTS.md` | 0 | `17063` bytes, 124 lines (bound 20,000 / 170) |

## Review status

Row 7 ran through the Fable 5.1 subagent route the user authorized (`human-review-decision.md`).
Round 1 returned `approved` with four non-blocking findings. The user directed them to be
addressed. The corrections are in `2affab6`, and Round 2 (reviewed state `abf0db9`) returned
`approved` with 0 open findings. The approval was read back:
`OK: approved at round 2 of 6, 0 open blocking findings`. H2 closeout (reflection, metrics)
remains.
