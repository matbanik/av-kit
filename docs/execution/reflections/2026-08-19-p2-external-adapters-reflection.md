---
date: "2026-08-19"
project: "p2-external-adapters"
meus: ["MEU-6", "MEU-7", "MEU-9"]
plan_source: "docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md"
template_version: "2.0"
---

# 2026-08-19 Meta-Reflection

> **Date**: 2026-08-19
> **MEU(s) Completed**: MEU-6, MEU-7, MEU-9
> **Plan Source**: docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   Plan review already took four rounds (ONNX hybrid + `check_exec_review.py`) before this execution pass. Exec r1 still found three High runtime holes the mocked suite had not named: NaN/`inf` yt-dlp byte counters aborting `_progress_hook`, file-mode `PermissionError` mapped to generic `DomainError`, and PyTorch `KModel` constructed on CPU while status claimed CUDA. Catalog `kokoro` string literals in Session 2 `engine.py` also false-failed a naive `rg -e kokoro` SCAN until catalog maps lived under `tts/voices.py`.

2. **What instructions were ambiguous?**
   `SCAN_ADAPTER_LIBS` allow-path `tts` for `kokoro` vs Session 2 seed ids in `database/engine.py`. The approved plan says catalog ids may live under `tts/`; do not rewrite `engine.py`. Cursor `plan_to_exec_gate: reviewer-auto` in `harness.local.md` still conflicts with create-plan §5c prose that calls that flag Antigravity-only. `execution-critical-review.md` HARD STOP says the reviewer must not chain corrections; the implementer loop in `task.md` H1-7 requires it.

3. **What instructions were unnecessary?**
   Restating the three handoff filenames in both plan and task (HANDOFF_GLOB already names the set). `delegate_to: av-kit-builder` on TDD rows while `fresh_worker: none` forbids isolated workers — recorded, never used.

4. **What was missing?**
   `tools/validate_closeout_artifacts.py` is still absent; named marker receipts (`HANDOFF_GLOB`, `PER_MEU_HANDOFF_AC`, `CHECK_EXEC_REVIEW`) substituted. The first AC-6.17 suite only skipped NaN *speed*, so RULE-1 on other numeric progress fields was not an executable oracle until exec r1.

5. **What did you do that wasn't in the prompt?**
   Continued from the user's `proceed with the review correction loop until codex gives approved` through H1 closeout, Codex exec r1 `changes_required`, failing regressions + adapter fixes for F1–F4, Codex r2 `approved`, and H2. Did not start Session 4 (`p3-services` / MEU-10). Did not commit.

### Quality Signal Log

6. **Which tests caught real bugs?**
   After r1, the added AC-6.17 NaN downloaded / `inf` total ticks, AC-6.18 existing-but-unreadable cookie `PermissionError`, and AC-9.4 `.to()`/`.eval()` tracking fakes. Independent Codex probes (`p2-ea-exec-r1-progress-probe.txt`, `p2-ea-exec-r1-cookie-unreadable-probe.txt`, `p2-ea-exec-r1-tts-device-probe.txt`) found all three before the original suite did.

7. **Which tests were trivially obvious?**
   AC-6.15 originally patched `_read_ytdlp_version` then asserted the patched return — tautological. Strengthened to monkeypatch `yt_dlp.version.__version__` and call the real helper. Left prior assertions in place (G36).

8. **Did pyright/ruff catch anything meaningful?**
   Neither caught F1–F3. Ruff on tests flagged I001/E501 in files I edited; the registered gate only lints `packages/infrastructure` and `packages/core` and stayed clean (`0` pyright, ruff all passed).

### Workflow Signal Log

9. **Was the FIC useful as written?**
   Named locks (`ONNX_PREPROCESS`, `COOKIE_MODES`, `SABR_LOG_NEEDLES`, `ENGINE_BY_FORMAT`, no `mark_downloaded`) prevented port mutation and WAV writes. The FIC said skip NaN progress but named *speed* in the AC-6.17 test more clearly than downloaded/total bytes — that gap became exec F1. Device Auto was specified for resolution, not for `KModel.to(device).eval()`.

10. **Was the handoff template right-sized?**
    Three MEU files each restated the 113-test gate. Usable; a shared receipt table would shrink them. Round-2 reviewer noted clerical `Corrections Applied: 0/0` left on the MEU handoffs (non-blocking; write-scope was the rolling review file).

11. **How many tool calls did this session take?**
    High hundreds across TDD, H1 receipts, two Codex dispatches (~12 min + ~9 min), F1–F4 corrections, and H2. Not optimized.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    None. `fresh_worker: none` forbade isolated builder rows. Codex ran reviews only (`gpt-5.6-sol`, high).

---

## Pattern Extraction

### Patterns to KEEP
1. Capture adapter-built `session.run` kwargs (phonemes `"ab"` → `[[0,1,2,0]]`) instead of fabricating feeds inside the test double.
2. Isolated `p2-ea-exec-rN-*` Codex receipts; never leftover census/p1/persistence-io files as current proof.
3. `check_exec_review.py` on the **first** YAML frontmatter only (`review_mode: implementation`, exact `target_plan`, `findings_count: 0`).

### Patterns to DROP
1. Progress hooks that `int()` yt-dlp counters after checking only `speed` for finiteness.
2. Mapping all `OSError` from `YoutubeDL` to generic `DomainError` when cookie mode is `file`.
3. Reporting a resolved TTS device in status without calling `KModel.to(device).eval()`.

### Patterns to ADD
1. Skip every non-finite numeric field on a progress payload *before* conversion or callback (downloaded, total, speed).
2. File-mode cookie IO: pre-open plus `CookieTestError from OSError` on the download path.
3. Tracking fakes for `.to` / `.eval` on every `SEED_VARIANT_IDS` PyTorch load, including Auto→CUDA/MPS.

### Calibration Adjustment
- Estimated time: one Session 3 TDD cycle after plan r4
- Actual time: TDD + H1 + exec r1/r2 + H2
- Adjusted estimate: budget an independent numeric/error-provenance/device-application adversary pass before first exec review of any library adapter

---

## Next Session Design Rules

```
RULE-1: Skip every non-finite numeric field on a library progress payload before int()/callback.
SOURCE: exec-review F1
EXAMPLE: NaN speed skipped but NaN downloaded_bytes raised ValueError → `_finite_int` then skip
```

```
RULE-2: Cookie-file IO failures during download are CookieTestError from OSError, not DomainError.
SOURCE: exec-review F2
EXAMPLE: existing file + PermissionError from YoutubeDL → DomainError → CookieTestError from PermissionError
```

```
RULE-3: Apply the resolved PyTorch device with model.to(device).eval(); status must match.
SOURCE: exec-review F3
EXAMPLE: load_model stored device=cuda while KModel stayed on CPU (map_location='cpu')
```

---

## Next Day Outline

1. `/create-plan p3-services` (MEU-10 DownloadService first; grouping Session 4) — do not invent IDs
2. No frozen-port mutations; no rewrite of Session 2 persistence or Session 3 adapters
3. Bake NaN/inf progress, cookie `__cause__`, and device `.to()/.eval()` probes into the first service FIC where those adapters are called
4. Codex validation on SABR session lock / archive skip (MEU-10), not a re-review of yt-dlp internals
5. Time estimate: one Session 4 plan + TDD cycle
6. Keep `uv sync --all-packages`; plain `uv sync` drops member deps

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | high hundreds (TDD + 2 exec reviews + H2) |
| Time to first green test | MEU-6 scaffold red then mocked YoutubeDL green |
| Tests added | 113 registered (domain + Session 2 + MEU-6/7/9); r2 strengthened 7 IR-5 tests in place |
| Codex findings | plan r4 approved (prior); exec r1 F1–F4 (3 High, 1 Medium); r2 approved 0 findings |
| Handoff Score (X/7) | 7/7 structural markers on all three MEU handoffs |
| Rule Adherence (%) | 90 |
| Prompt→commit time | n/a (no commit; draft only) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Redirect every shell stream to C:/Temp/av-kit | AGENTS.md §P0 | Yes |
| Tests first; do not neutralize assertions | AGENTS.md §TDD / G36 | Yes |
| Never self-review; dispatch Codex | AGENTS.md §Execution Contract | Yes |
| Never auto-commit | AGENTS.md §Commits | Yes |
| Anti-premature-stop: H1→review→H2 one pass | AGENTS.md §Execution Contract | Yes |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "bd1252fe-228d-485e-957e-9cb17f660df8"
  task_class: tdd
  outcome: success
sections:
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: execution_contract
    cited: true
    influence: 3
  - id: testing_tdd_protocol
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 1
  - id: dual_agent_workflow
    cited: true
    influence: 2
  - id: code_quality
    cited: true
    influence: 2
  - id: pre_handoff_self_review_mandatory
    cited: true
    influence: 1
  - id: windows_shell_powershell
    cited: true
    influence: 2
  - id: instruction_coverage_reflection
    cited: true
    influence: 2
loaded:
  workflows: [execution_critical_review, tdd_implementation]
  roles: [orchestrator, coder, tester]
  skills: [cli_dispatch, quality_gate, completion_preflight]
  refs:
    - docs/build-plan/02-infrastructure.md
    - docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md
    - .agent/context/harness.local.md
    - .agent/skills/cli-dispatch/SKILL.md
    - tools/check_exec_review.py
decisive_rules:
  - "P0:redirect-all-streams-to-C:/Temp/av-kit"
  - "P0:independent-review-no-self-review"
  - "P1:tests-first-do-not-edit-assertions"
  - "P1:anti-premature-stop-H1-review-H2"
  - "P1:frozen-ports-unmutated"
conflicts:
  - "execution-critical-review.md HARD STOP (reviewer must not chain corrections) vs task.md H1-7 implementer loop — followed H1-7 as driving closeout"
  - "create-plan §5c reviewer-auto described as Antigravity-only; harness.local sets reviewer-auto for Cursor"
slim_candidate:
  - dual_agent_workflow
  - "HANDOFF_GLOB filenames restated in both plan and task"
overthinking_observed: false
review_churn:
  rounds_to_approval: { plan: 4, execution: 2 }
  findings_per_round:
    - { round: 1, critical: 0, high: 3, medium: 1, low: 0 }
    - { round: 2, critical: 0, high: 0, medium: 0, low: 0 }
  churned_findings: 0
  finding_categories:
    boundary_validation: 1
    contract_drift: 2
    weak_test: 1
  verdicts:
    changes_required: 1
    approved: 1
meu_work_classes: [correctness, correctness, correctness]
```
