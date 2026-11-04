# Planning walkthrough — framework update adoption

Scope: inspect the local framework checkout, compare it with current av-kit, prioritize useful updates and produce a reviewed adoption plan. This artifact records planning work; it is not implementation evidence for AC-1–AC-9.

## Evidence

Observed September 26, 2026. Full commands used `rtk proxy`, PowerShell `*> C:/Temp/av-kit/<receipt>`, immediate `$LASTEXITCODE` capture, receipt read and exit propagation.

| Check | Observed result |
|---|---|
| Source identity | `003929c1cafa83359f0695415bbc06074a35f92e`; source `git status --short` exit 0, no entries |
| Destination identity | `a841d46308bcb58b6467d58db2d95175fe90fd91` plus pre-existing dirty worktree; HEAD alone does not identify reviewed input |
| Tracked core comparison | 130 entries: 17 missing, 74 different, 38 equal, 1 binary; full inventory saved as a draft artifact in this folder, not added to Git index |
| Missing tools | Actual search for `tools/validate_closeout_artifacts.py` produced exit 2 / file-not-found; inventory confirms absence alongside task linter, ledger and evidence dependencies |
| Context tool eligibility | Both graph files absent in both repositories; Headroom unavailable; `not_applicable`, no new decision gate |
| Reviewer prerequisites | `codex login status`: `Logged in using ChatGPT`; `codex --version`: `codex-cli 0.157.0`; both exit 0 |
| Initial document inspection | `python C:/Temp/av-kit/check_adoption_plan_docs.py`: exit 0; 11 required plan sections, 19 implementation rows all unstarted, 9 unique ACs, complete 130-row inventory, no structural errors |

The document inspector was an external scratch script that only read the new plan files and printed results. It did not execute repository tooling or product tests. It checked sections, task dependency order, column counts, unstarted status and inventory arithmetic; it does not replace independent semantic review.

## Changed Files

Only new planning/review/closeout artifacts for this project are authored during this session. No framework feature is installed, no product file is edited, and existing project focus/SSOT/metrics are not rewritten for this planning-only request.

| Artifact | Purpose |
|---|---|
| `implementation-plan.md` | Dependency-ordered selective adoption with source-backed ACs, compatibility, validation and rollback |
| `task.md` | Future implementation and H1/review/H2 rows, all unstarted |
| `upstream-assessment.md` | Prioritized comparison, evidence and source limitations |
| `upstream-inventory.json` | Per-file normalized tracked core inventory |
| `planning-walkthrough.md` | Planning observations and review/correction evidence |

## Review

The existing local CLI wrapper is used for this plan review; the future registry/ledger policy is not installed. The reviewer uses a separate context but the same vendor as the plan author, as disclosed in the prompt. The actual verdict belongs to the rolling `.agent/context/handoffs/2026-09-26-framework-update-adoption-plan-critical-review.md` report. No implementing agent may author its own approval.

## Execution boundary

The request is planning-only. A plan-review approval does not execute any task row. Product Session 24 remains the next product work in current-focus; this governance plan is separately available for explicit adoption direction.

## Interrupted review and pre-verdict corrections

The first dispatch (`framework-adoption-plan-r1-20260926`) ended without `status.json`, a final response or a reviewer-authored report. Its execution handle disappeared and a process-owner inspection found no surviving reviewer for that dispatch. This is an interrupted attempt, not an approval or completed review round. The user's `continue` resumed the planning task.

Its stderr contains the concrete loader observation: `project doc exceeds remaining budget; truncating path=file:///P:/av-kit/AGENTS.md remaining_bytes=32768`. This is evidence about that Codex invocation only; no universal harness-loading limit is inferred. Other MCP startup warnings did not prevent source reads before interruption.

Static source inspection also found two draft command issues before a verdict: upstream `Test-CliDispatch.ps1` defaults to `-Test all`, which includes live providers, and the combined pipeline tests import a ledger/adapter/schema not installed until WP-4. V9 now explicitly selects provider-free `wrapper-contract`; WP-1 uses the evidence-only V16 and leaves V5 for WP-4. Added exact lint/type commands and the compiled overlay/provenance destination based on the live resolver source. No project checks were executed to obtain these observations.

The replacement round-1 dispatch is `framework-adoption-plan-r1b-20260926`, launched through the same existing wrapper using a hidden background PowerShell process so the review can persist across a conversational interruption. The original receipt directory remains intact.

## Concurrent repository activity

A status comparison later showed existing dirty entries disappearing and a separate `2026-09-26-p11-queue-pages/` plan appearing. Read-only Git history confirmed a new HEAD `2e4c308`, preceded by `17230ca` and `0e4025e`. The planner did not run any Git mutation. SHA-256 checks for AGENTS, GUARDRAILS, the legacy execution-review checker and pyproject still exactly match their initial values. Current-focus still identifies the approved Session 23 outcome and Session 24 next work. This concurrent commit sequence is not evidence that files were deleted or that this planner owns those changes. Future adoption must capture a fresh working-tree baseline.

## Round 1 corrections and census

Independent round 1 found three High issues; all confirmed by direct source reads. The corrected bootstrap now has explicit capture → Red → helper → baseline verification rows, with tests selected by dependency stage. The final gate commands are complete in task cells and correlate report, original verdict, dispatch status and ledger (or a genuine named-human decision). The model plan uses five add-only project classes with explicit existing bindings; it does not redefine global classes or silently adopt the shared registry's different defaults. Operational routing documents found outside the original allowlist are now included.

The wrapper's child completed with exit 0 and a real report/JSON, but wrapper exit was 1: `can't open file 'P:\\av-kit\\tools\\validate_json_schema.py': [Errno 2] No such file or directory`. Validation via `uv run python -B C:/Temp/av-kit/validate_adoption_review.py C:/Temp/av-kit/dispatch/framework-adoption-plan-r1b-20260926` exited 0: `round=1`, `verdict=changes_required`, `findings=3`, `target_bound=true`, `json_schema_checked=true`. The original failure is retained; no successful-wrapper claim is made. Round 2 uses the supported Markdown output route without `-OutputSchema`, then verifies the canonical report's frontmatter directly.

Correction census: three contract families plus dependency selectors were swept across **both** plan files, with old and new forms (bootstrap helper/row 0/V1/1a/1b; review-state/approved-state/V19/cap; class names/active surfaces/omitted workflow and lifecycle docs; V20–V24). Full untruncated path/line matches are in `C:/Temp/av-kit/adoption-r1-correction-census.txt`; old-form scan is `adoption-r1-old-patterns.txt`. The old helper-before-tests and deferred approval-command text are absent. One stale current handoff row count was updated to 21; historical initial 19-row observations remain labelled as initial. The `19 task` regex also matches `V19 task` in the command definition, confirmed as a false-positive, not a stale row count.

The active operational source census is `C:/Temp/av-kit/adoption-active-routing-census.txt`; all 35 matched paths were classified as planned operational merge surfaces or preserved historical/test data. A full content/line census and negative stale-routing fixtures are explicit future execution deliverables; no claim of already-migrated routing is made. Current scratch inspection passes: 11 sections, 21 unstarted rows, 9 ACs, 130 inventory entries, no structural errors.


## Round 2 correction audit

Round 2 returned one procedural PR-6 issue: the raw correction census lacked per-site dispositions, so the reviewer did not adjudicate the three corrected substantive findings. The rolling review now contains 48 individually dispositioned sites covering all 84 original match lines. Every site was checked against current plan/task text, including substring matches and repeated tokens. No plan behavior changed for this correction. Round 2 wrapper exit was 0. Round 3 is the final permitted plan-review pass; adoption remains unstarted.


## Planning completion

Independent Round 3 approved the canonical plan with zero findings. Dispatch `framework-adoption-plan-r3-20260926` completed with wrapper exit 0 and child exit 0. Target/mode/round/verdict/count and status were checked directly, not inferred from successful dispatch. The scratch document and artifact inspectors passed: 11 plan sections, 21 unstarted execution rows, 9 ACs, 130 inventory entries and required handoff/reflection markers. No adoption tools, product tests, commits or implementation rows were executed. The reviewed proposal is ready for a separate user execution instruction; product work and concurrent files remain outside this planning task.
