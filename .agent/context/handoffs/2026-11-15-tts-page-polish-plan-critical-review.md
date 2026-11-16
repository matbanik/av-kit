---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-tts-page-polish/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "tpp-plan-2026-11-15-tts-page-polish"
round: 1
---

# Critical Review: 2026-11-15-tts-page-polish

> **Review Mode**: `plan`
> **Verdict**: `approved`

## Intent Anchor

the TTS page shows a job's progress as a percentage and never calls the 1000-step progress scale segments; each TTS output file keeps a name that says what the clip is and never overwrites a file already in the folder; and every TTS status pill label reads at 4.5:1 or more against its fill in both themes, which Mat confirms by looking at both themes before it ships.

Executing this plan and satisfying its rows would deliver that objective. No evidence-backed High or Critical delivery defect was found.

## Scope

Reviewed the complete implementation plan and task, all eight plan-local scripts, Session 80's grouping and three issues, the cited build-plan homes and rc.3 F5 ruling, HDP decisions D-955 through D-963 and the expert-pass receipt, current TTS renderer/service/domain code, the shared chip/bar/tokens, and the relevant existing test assertions and fixtures. Applied PR-1 through PR-9 and the Materiality Gate. The actual renderer paths are under `ui/src/renderer/src/features/tts/`, as the plan inventories.

This is readiness approval of an unstarted plan. No pytest, Vitest, npm, dependency synchronization, Electron launch, provider dispatch or network request ran. Repository files were read only; all review writes are under `C:/Temp/av-kit`. The identity helper's live whole-tree mode was inspected, not executed; no forbidden local settings or secret file was opened. The coordinator must copy this report to the canonical review path.

| Reviewed file | SHA-256 |
|---|---|
| implementation-plan.md | f55c0a96ab9e50e2827d07885872e6f3bd3ed440c9758d7df43d7a16832e964c |
| task.md | c900bd22c2a8b3fecfd5de19e6ca809f5731e337d705e1cacd2e37002d8d83b2 |

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Goal and acceptance coverage

Accepted. Each goal clause has observable ACs and ordered execution rows:

| Goal clause / contracts | ACs | Rows |
|---|---|---|
| PROGRESS_PERCENT and PROGRESS_ARIA | AC-150.1–AC-150.3 | 1–2, H1-2 |
| No scale-as-segments wording in 06; updated F5 output example | AC-150.9 | 6 |
| NAME_SCHEME_KEPT, NAME_SAFE_GUARD, NAME_COLLISION_GUARD, LEGACY_OUTPUT_KEPT | AC-150.4–AC-150.7, existing F5 tests | 1, H1-2 |
| API_SHAPE_UNCHANGED | AC-150.8 | H1-2, H1-4 |
| PILL_CHIP_TONES, PILL_LABEL_KEPT, STATUS_COLORS_RETIRED | AC-149.1–AC-149.4 | 3–4 |
| PILL_CONTRAST_TEST and QUEUE_TOKENS_UNCHANGED | AC-149.5–AC-149.7 | 3–4, H1-2, H1-4 |
| THEME_CHECK and Mat's recorded confirmation | AC-149.8, D-806 | 5–6 |

The rc.3 ruling and shipped code justify retaining F5 and adding guards rather than changing Python product code. The plan correctly explains why the later-registered 03 description was already stale. No required goal clause is silently deferred.

## Q2 — Progress and output-name guards

Accepted D-959 and D-963. The shared floored/clamped percentage gives 0% at zero or invalid total, 0% for non-finite inputs, 99% at 999/1000 and 100% at 1000/1000. Passing the same integer divided by 100 to the unchanged ProgressBar makes its rounded accessible value agree with the label (`ProgressBar.tsx:78–86`). A scratch JavaScript calculation probe covered 15 normal, boundary and non-finite cases; this verifies the planned calculation, not future exports.

The existing `test_output_stem` pins the precise F5 names; existing generation tests pin MP3/WAV names and successive -2/-3 suffixes. New guards add forbidden/control/device-name inputs, direct output-parent assertions, speech fallback, legacy bytes/UUID preservation, and both lone user-owned WAV and MP3 collisions. `_Stack` writes real scratch files through its filesystem/media fakes, so an overwrite changes the asserted bytes; a wrong stem changes the asserted output path. These are effective oracles, not checks of a mocked naming helper. AST-isolated probes of the current source definitions independently confirmed safe stems and -2 selection for both extensions.

D-957 explicitly preserves serialized service allocation and records the existing race with an unrelated program creating a file after selection. Approval does not claim exclusive-create protection; that disclosed residual is outside this guard-only change.

## Q3 — Status mapping, contrast and consumers

Accepted D-956 and D-960. The proposed six keys cover all five backend `TTSStatus` values plus the page's Idle state. An unknown readable string reaches a neutral chip; the explicit empty-string default prevents StatusChip's readable-label exception. The plan tests that empty-string regression. Type-only imports introduce no runtime dependency cycle.

The contrast test contract reads the real StatusChip fill/alpha/text classes and live theme tokens, overlays light values on the dark defaults, and checks all six statuses over all three page/card surfaces in both themes. A single opaque colour mixed with transparent at /10 retains its colour and has 10% alpha; source-over channel composition models that tint. Independent source probes found all 36 ratios above 4.5, with the minimum **6.862891:1**, dark Generating over bg-elevated. The old solid dark Generating pair is **1.298495:1**, matching the proposed failing calibration.

The renderer-wide STATUS_COLORS census contains only the two TTS files and transcript-controls. Retiring the TTS export/import therefore leaves no other source consumer broken; the named AC-22.24 and AC-43.2 assertion updates account for the test consumers. Shared tokens, chip and bar remain byte-bound to row 0.

## Q4 — Red/Green and session gates

Accepted. Row 1's absent exports and old text/ARIA produce the required assertion failures; the already-shipped Python guards are honestly PASS_TO_PASS. Row 3's absent tone export, old export/census and missing pill test ID produce assertion failures; its contrast test asserts export presence before use. The calibration may already pass, while the matrix test supplies the required AC-149.5 failure. The checker requires each listed AC to fail by assertion and rejects setup errors. Its independent selftest returned **64 fixtures, 0 wrong**, including 44 negative fixtures.

Only AC-56.5, AC-22.24 and AC-43.2 existing assertions change, with the precise replacements specified before execution. The same AC-56.5 prefix also occurs on other tests, but the checker still requires an actual failed assertion and the task names the exact changed title. No extra assertion change or undisclosed M-7 choice is needed.

PowerShell/npm --prefix selects the UI package as the script working directory; `baseline.ps1` also explicitly Push-Locations to ui. Python runs through uv run pytest. The fail-fast session script covers Python lint/format/types, UI types/lint, targeted Python/UI cases, full suites, OpenAPI and register checks, compiled UI, then the existing real Electron TTS test with ELECTRON_RUN_AS_NODE cleared. It rejects targeted Python skips, excuses only recorded baseline Python failure IDs, excuses no UI failures, and compares before/after input identities. These future Red/Green and runtime results were not claimed executed during this review.

## Q5 — Ordering, content baselines, writes and registers

Accepted. Baseline copies and SHA-256 manifests capture actual row-0 working bytes; S2 tests edit anchors rather than clean-tree/HEAD equality. S4 preserves unrelated dirty content; `readonly-check.py` compares protected sources and dirty package/MCP inputs to row 0. A scratch fixture accepted a package source marked dirty at row 0 and returned failure for a mismatched expected content hash. This confirms the important earlier-session case without changing repository files. A moved HEAD may conservatively invalidate gate identity; it does not redefine Session 80's diff base.

Byte writes and explicit CRLF checks protect the seven modified CRLF files, with additional checks on shared closeout state. Declared edits remain in the inventoried product/tests/docs/register entries, plan and closeout artifacts; dependency/build/test effects are explicitly scheduled. Issue resolution calls the issue-triage model, restricts parsed changes to the three issues' status/verification/resolution fields, checks the row-0 hash and holds an exclusive Windows handle. MEU updates/rendering use tools/meu_status.py. No new non-handable M hit was demonstrated in the delegated briefs.

Row 5 gives Mat concrete Idle/Generating/Done-or-Cancelled steps in both themes and accepts only recorded approval before rows 6–7. The process helper identifies Electron by the av-kit executable directory, records launch ancestry and creation times, excludes MCP/checker/foreign processes, and rechecks creation time before a PID kill. Its selftest returned **0 failures**, including orphan and PID-reuse cases. No live process was queried or stopped by this review.

The latest trusted user instruction already authorizes execution after approval; stale generic wording about another authorization message does not override it. Session 87 must close and commit first, then Sessions 75–79 precede this one. Session 80 remains uncommitted with a message draft, as instructed.

## Checklist Results

Results concern plan readiness. Manual observer: `codex-independent-reviewer`; manual exits are null.

| Check | Result | Procedure / observation | Exit |
|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compared full plan, task rows 0–7 and H1/H2, AC mapping and script argv | null |
| PR-2 Not started | pass | Task rows unchecked; current renderer retains old label/map; new contrast test scheduled for creation | null |
| PR-3 Task contract | pass | Inspected owners, deliverables, commands, dependencies and statuses | null |
| PR-4 Validation realism | pass | Traced gate scripts, fixture behavior and npm package script cwd; ran safe checker/source probes | null |
| PR-5 Source-backed planning | pass | Compared F5, 03/06 rules, grouping, issue decisions, HDP and expert-pass receipt | null |
| PR-6 Handoff/corrections readiness | pass | Two MEU handoffs and one target-bound independent execution review explicitly ordered | null |
| PR-7 Scope discipline | pass | Guard-only names match F5; queue tokens, API and legacy files preserved; residuals explicit | null |
| PR-8 Reachability and negative oracles | pass | Traced page to helpers/chip/bar and service worker to output_stem/_free_paths/writers; checked concrete failure assertions | null |
| PR-9 Single-statement contracts | pass | Named contracts govern task references; no materially conflicting live behavior definitions found | null |
| Product suites and Mat's visual check during review | n/a | Prohibited or future execution obligations; no execution pass asserted | null |

### Executed probe evidence

```json
{"schema_version":"evidence.v1","check_id":"tpp-review-safe-selftests","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/tts-page-polish/review/run-safe-checks.ps1","cwd":"P:/av-kit","scope":"plan-local red-check.py and dev-app-procs.py synthetic selftests","phase":"targeted","exit_code":0,"result":"pass","tested_state":"review-round-1-current-plan-scripts","output":"red-check selftest: 64 fixture(s) (20 positive, 44 negative), 0 wrong: []; dev-app-procs selftest: 0 failure(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"tpp-review-source-probes","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/tts-page-polish/review/source-probes.py","cwd":"P:/av-kit","scope":"selected shipped naming definitions, current chip/token source, tool existence and synthetic readonly baseline","phase":"targeted","exit_code":0,"result":"pass","tested_state":"review-round-1-current-named-sources","output":"source name guards: 8 unsafe inputs, F5 scheme and speech fallback pass; lone WAV and lone MP3 both select -2; source contrast: 36/36 >= 4.5; worst=6.862891 dark/Generating/bg-elevated; negative calibration=1.298495; 8 plan-local scripts present, 6 referenced tools exist; readonly fixture accepts row-zero dirty content and refuses mismatched expected content","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"tpp-review-progress-calculation","command":"rtk proxy node C:/Temp/av-kit/tts-page-polish/review/progress-probe.mjs","cwd":"P:/av-kit","scope":"scratch evaluation of specified percentage and existing ProgressBar rounding formula; not future product implementation","phase":"targeted","exit_code":0,"result":"pass","tested_state":"review-round-1-planned-progress-formula","output":"planned progress calculation: 15 cases pass; label number equals ProgressBar aria-valuenow","fresh":true}
```

All probe processes set PYTHONDONTWRITEBYTECODE=1; temporary directories and output stay under the review scratch directory. The first source-probe attempt stopped on the review probe's own table-indentation matcher; correcting that scratch-only matcher produced the recorded complete pass. It was not a product or plan failure.

## Verdict

**approved** — 0 findings. The plan is ready for execution in the authorized grouping order. Execute its actual Red/Green/full gates, preserve the content baselines, and retain the explicit stop for Mat's look in both themes. Approval certifies the plan's design and validation contract; future implementation and runtime passes remain to be produced.
