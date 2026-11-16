---
date: "2026-11-16"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-15-tts-page-polish/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "tpp-execution-2026-11-15-tts-page-polish"
round: 1
---

# Critical Review: 2026-11-15-tts-page-polish

> **Review Mode:** execution
> **Verdict:** approved

## Scope

Session 80, MEU-150 and MEU-149: the implementation plan, task, plan-local scripts and baseline data, human-check record, both MEU handoffs, product/test deltas, new contrast test, register and build-plan changes, and the named receipts. Baseline is `771c279624d7b99aebab6285d945ca6317605486`; row-0 copies were hash-verified. Sessions 81–83's planning artifacts were excluded. Applied IR, relevant DR, and AV-1–AV-6. Codex is the independent reviewer; Anthropic authored the work.

**Intent anchor:** “the TTS page shows a job's progress as a percentage and never calls the 1000-step progress scale segments; each TTS output file keeps a name that says what the clip is and never overwrites a file already in the folder; and every TTS status pill label reads at 4.5:1 or more against its fill in both themes, which Mat confirms by looking at both themes before it ships.”

**Intent achieved:** yes, within the approved contracts and exclusions. No Critical, High, or other actionable finding was established.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Progress label and accessible value

Accepted `PROGRESS_PERCENT` and `PROGRESS_ARIA`. `tts-controls.ts:24` implements the finite-input/positive-total guard and a floored, 0–100 clamp; `progressLabel` and `progressFraction` share that function. `TTSPage.tsx:301` and `:737–742` use the same job fields for bar and label. The preview/hash remain, and the bar is named `Generation progress`. A scoped source search found no remaining rendered raw count or `Segments` label; API fields, polling intervals, comments and compatibility test IDs are not displayed progress labels.

An independent Node probe evaluated the actual helper source: 54 boundary combinations passed, including zero/negative totals and NaN/positive/negative Infinity in either input. All 101 whole percentage values survive ProgressBar's rounding unchanged; 999/1000 gives text `99%` and `aria-valuenow=99`. Accepted AC-150.1–AC-150.3; no failure found.

## Q2 — Output names and Python fidelity

Accepted `NAME_SCHEME_KEPT`, `NAME_SAFE_GUARD`, `NAME_COLLISION_GUARD`, `LEGACY_OUTPUT_KEPT` and `API_SHAPE_UNCHANGED`. The shipped `domain/tts.py:369–385` keeps the first three cleaned words and voice suffix; `services/tts.py:84–96` checks both WAV and MP3 before choosing a suffix. No Python product, API, schema or MCP change exists. Both Python files match row-0 bytes and Git's filtered HEAD checkout bytes. Raw Git blobs use Git's line-ending representation; this is not an execution edit.

The guards at `test_tts_output_name.py:122–174` are substantive. Every unsafe-text parameter is passed to `output_stem` and through actual `TTSService` generation, then checked for containment, exact filename and directory contents. The helper waits for idle and requires Done. Unsafe text is placed where it can affect the name. Collision cases begin with exactly one user-owned MP3 or WAV, require `-2`, and compare the original bytes. The legacy case compares UUID-file bytes, exact new output path and UUID4 identity. `_require` asserts service capabilities; it does not skip tests. Existing fixed name examples prevent an always-`speech` implementation from satisfying the suite.

The new guards passed when written: **23 passed**, as S7 requires; targeted gate tests later report **61 passed** without skips. Independent OpenAPI `--check openapi.committed.json` exited 0. Accepted AC-150.4–AC-150.8. The approved D-957 external-writer race exclusion remains: these checks do not establish exclusive-create reservation against another program creating the same name between check and write.

## Q3 — Pill mapping, label and unchanged primitives

Accepted `PILL_CHIP_TONES`, `PILL_LABEL_KEPT`, `STATUS_COLORS_RETIRED` and `QUEUE_TOKENS_UNCHANGED`. `tts-controls.ts:63` matches the six-row table exactly: Idle/Cancelled neutral, Pending warning, Generating info, Done success, Failed danger. `TTSPage.tsx:130` supplies Idle for the specified empty-string status, and `:725` passes the status label to StatusChip with a neutral fallback for unknown statuses. StatusChip additionally validates tone ownership before selecting classes.

The legacy map/import is removed; the test census now contains only transcript controls. The nine read-only baseline hashes match, including StatusChip, ProgressBar, status-tokens, styles, test IDs, TTS E2E and OpenAPI. Accepted AC-149.1–AC-149.4 and AC-149.6; no primitive/token regression was found.

## Q4 — Contrast test

Accepted `PILL_CONTRAST_TEST` and AC-149.5. `tts-pill-contrast.test.ts:41–74` reads real CSS tokens and overlays light overrides on dark defaults. The current blocks are flat and match its parser. At `:98–119` the test renders the shipped StatusChip, extracts its actual fill token, alpha and text-color class, and requires exactly one of each. At `:127–145` it iterates the real six-status list across three backdrops in both themes and requires exactly 36 pairs, each at least 4.5 without ratio rounding.

The source-over, half-up sRGB composite and WCAG luminance calculation at `:77–94` match the approved model. The old-solid calibration at `:148–153` is below the floor. Independent calculation from the production sources found **36 pairs, zero below 4.5**; worst **6.86289098:1**, dark Generating over bg-elevated. Light spans **11.38889066–13.50327394:1**. Old-solid calibration is **1.29849497:1**. A scratch low-contrast control measured 1:1 and was rejected. A low-contrast shipped token/class pair would enter the below-floor array and fail; colors are not copied into fixed test constants.

## Q5 — Red, Green and full gate

Accepted the assertion-based Red proof and matching Green evidence. Replayed both original receipts through `red-check.py`: MEU-150 has **4 required tests, zero problems**; MEU-149 **5 required tests, zero problems**. Their original child exits are 1. The failures are the intended missing-export, old text/ARIA, legacy-map and missing-chip assertions, with no setup failure accepted. The independently rerun checker selftest reports **64 fixtures, 20 positive/44 negative, zero wrong**.

Green receipts report **65 passed** for MEU-150 and **104 passed** for MEU-149. D-964 is sound for this run: both Red inputs are Vitest; Python guards are expected-pass checks and never reach red-check. The retained pytest-header limitation cannot invalidate these observed Red inputs.

`tpp-gate-h1.txt` contains all **20 required steps at exit 0**, with all individual receipts present and matching identities before/after. Full results: **3008 Python tests**, **1547 UI tests in 133 files**, **23 real Electron TTS tests**; static, targeted, build, OpenAPI and render checks pass. No baseline failure was excused. MCP skips are justified by unchanged MCP/API shape; build-record is skipped because this is not a distribution build. The UI build did run.

| Test surface audited | Rating | Basis |
|---|---|---|
| Python filename guards and existing scheme tests | Strong | Exact outputs, real service paths, original-file bytes and containment |
| tts-page helper/map tests | Strong | Concrete boundary outputs and complete ordered tone table |
| tts-page behavior tests | Strong | Rendered text, ARIA, transitions, tint classes and empty-status recovery |
| New contrast tests | Strong | Real component/classes/tokens, complete matrix and failing calibration |
| Changed queue census assertion | Strong | Exact residual source inventory, paired with unchanged primitive regressions |

Only the three existing assertions named under M-7 changed: AC-56.5, AC-22.24 and AC-43.2. Their fixtures and unrelated assertions remain. No weak test, expectation neutralization or hidden deferral was found. Product suites were inspected through receipts, not rerun by this reviewer.

## Q6 — Registers, MEU state and documentation

Accepted AC-150.9, AC-149.8 and `THEME_CHECK`. The resolution receipt records the named hash-bound tool, **15 permitted leaf-field changes**, and zero problems. Independent comparison confirms only status/verification/resolution fields of the three intended issues changed. Current register bytes equal the tool's staged file and recorded SHA-256. Independent `issue_triage.py render --check` reports `OK: known-issues.md is up-to-date`.

Both MEUs are `ready_for_review`; regenerated registry/BUILD_PLAN deltas agree. The grouping delta is exactly §6 row 80. Both build-plan documents retain CRLF; the revised wireframe lines keep their lengths. Delivered notes accurately describe the implementation and quote Mat's exact word, `approved`.

`human-check.md:3–28` satisfies row 5's record contract: approval decision, dated USER_EXPLICIT reference and verbatim answer, quoted request, faint-light-tint context, and launch record. Mat's choice is accepted as given. No second visual approval or reinterpretation of that choice is required.

## Q7 — Safety, scope and evidence fidelity

Accepted. Current scope-check reports **16 Files Modified paths**, **three unchanged baseline-dirty hashes**, and no outside-scope change. Scope files preserve their row-0 line-ending kinds; gate evidence separately confirms **17/17** configured files, including metrics and current-focus. Session additions contain no real home-folder path or personal email. The executor's scratch wrappers contain no commit, stash, revert, reset or push command; HEAD remains the baseline. No contrary action is evidenced. This reviewer edited no repository file and started/stopped no application process.

`dev-app-procs.py:135–154` classifies ownership from the recorded PID/creation-time tree and excludes MCP servers; `:215–223` rechecks creation time before stopping each owned process. Recorded stop IDs belong to that launch; the follow-up receipt shows **zero of this launch's left, zero others**. No process outside the launch is shown as stopped.

**Tested state:** `771c279624d7b99aebab6285d945ca6317605486+945866edc3525f301997037c3f7885c4b75175fc2f1621ee6307c037296c362d`.

This is the plan's `identity.py --state-only` result with ELECTRON_RUN_AS_NODE unset, and it matches the gate exactly. The sandbox's only disclosed ignore difference was handled with a process-local core.excludesFile pointing to a scratch file containing only `/.claude/settings.local.json`. Inherited Git configuration was preserved. The secret path and host global ignore were never opened or hashed. No secret-inclusive identity was calculated and no repository/global Git setting changed. Thus there is no remaining identity mismatch; the missing host ignore effect alone was restored.

Both handoffs contain all 9/8 own ACs and full evidence with that state. Handoff output counts, Red reasons, worst-pair values, register hashes and current source agree with the receipts. Disclosed departures do not establish a product defect. The post-approval Status-line edit does not alter an AC or contract; approval is based on the current plan/source/evidence, not reuse of the obsolete plan-text hash.

## Checklist Results

| Check | Result | Command or observed procedure | Exit | Evidence |
|---|---|---|---|---|
| IR-1/4/7 and relevant DR; all 17 own ACs | pass | Codex compared plan, both handoffs, source/diffs, test assertions and receipts | null | All ACs supported; no missing delivered behavior |
| IR-5; AV-1–AV-6 | pass | Codex assertion audit; red-check selftest and two receipt replays | 0 for checker commands; null for audit | 64 fixtures; 4/5 required Red tests; no problems or bypass |
| Progress behavior | pass | `rtk proxy node C:/Temp/av-kit/tts-page-polish/exec-review/progress.cjs` | 0 | 54 boundary combinations, 101 whole percentages, 999/1000 agreement |
| Contrast and data fidelity | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/tts-page-polish/exec-review/probe.py` | 0 | 36 pairs; worst 6.86289098; scope endings/read-only hashes/row 80/MEU states agree |
| Evidence and safety audit | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/tts-page-polish/exec-review/audit.py` | 0 | 20 step receipts; 9/8 unique ACs; matching full records; staged register bytes; additions scan clean |
| Read-only invariants / scope | pass | Plan `readonly-check.py` and `scope-check.py` with scratch ignore override | 0 each | Nine read-only files unchanged; packages/MCP: zero changed paths; scope-check: ok |
| OpenAPI and issues render | pass | `rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json`; `rtk proxy uv run python tools/issue_triage.py render --check` | 0 each | Schema unchanged; known-issues.md up-to-date |
| Full-gate freshness | pass | `identity.py --state-only`; Codex compared existing gate and individual receipts | 0 for identity; null for inspection | Current state equals both gate identities |
| IR-2/3/6 | n/a | No new stub, route or external write schema | null | API and Python product unchanged |

Python probes used PYTHONDONTWRITEBYTECODE=1 and scratch TMP/TEMP; uv checks additionally used offline/no-sync and a scratch cache. All shell output used RTK proxy, receipts and preserved exits. Initial reviewer setup attempts hit inherited-Git-config replacement, a wrong Red receipt filename/argument shape, uv cache access and an omitted OpenAPI check path; corrected invocations passed. A scratch comparison initially assumed raw Git blob bytes equal checkout bytes; accounting for core.autocrlf confirmed unchanged product files. None of those setup failures is treated as product evidence or hidden by a wrapper success.

```json
{"schema_version":"evidence.v1","check_id":"tpp-review-r1-progress","command":"rtk proxy node C:/Temp/av-kit/tts-page-polish/exec-review/progress.cjs","cwd":"P:/av-kit","scope":"Actual progress helper source, input boundaries and ProgressBar rounding","phase":"targeted","exit_code":0,"result":"pass","tested_state":"771c279624d7b99aebab6285d945ca6317605486+945866edc3525f301997037c3f7885c4b75175fc2f1621ee6307c037296c362d","output":"54 boundary combinations agree; all 101 percentage values agree with ProgressBar rounding; 999/1000: 99%, aria-valuenow 99","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"tpp-review-r1-probe","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/tts-page-polish/exec-review/probe.py","cwd":"P:/av-kit","scope":"Contrast from production tokens/classes; baseline bytes and endings; grouping and register deltas; human quote","phase":"targeted","exit_code":0,"result":"pass","tested_state":"771c279624d7b99aebab6285d945ca6317605486+945866edc3525f301997037c3f7885c4b75175fc2f1621ee6307c037296c362d","output":"36 pairs, zero below 4.5; worst 6.86289098 dark Generating bg-elevated; old calibration 1.29849497; low-contrast control rejected; 16 scoped endings preserved; nine read-only hashes unchanged; Python product matches filtered HEAD; row 80 only; three issues resolved through permitted fields; MEU-149/150 ready_for_review; human quote approved","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"tpp-review-r1-gate-observation","procedure":"Codex read tpp-gate-h1.txt, individual D6 receipts and both handoffs, then compared their states with independently executed identity.py --state-only using a scratch ignore override and ELECTRON_RUN_AS_NODE unset.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Existing fresh full gate for both MEUs, reused without rerunning suites","phase":"static","exit_code":null,"result":"pass","tested_state":"771c279624d7b99aebab6285d945ca6317605486+945866edc3525f301997037c3f7885c4b75175fc2f1621ee6307c037296c362d","output":"20 required steps exit 0; full Python 3008 passed; full UI 1547 passed in 133 files; real Electron TTS 23 passed; gate before/after/current identities match; no baseline failure excused"}
```

## Verdict

`approved` — the delivered work achieves the registered intent within the approved contracts. No correction is required. The coordinator can record this independent round and continue H2 and the authorized commit. This is review approval, not a claim that H2 or commit has occurred. Push remains unauthorized.

Residual limits remain the approved external-writer filename race and lack of pill status-change announcements. No new open question is needed.
