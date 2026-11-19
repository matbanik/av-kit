---
date: "2026-11-19"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-19-e2e-host-parity/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ehp-plan-2026-11-19-e2e-host-parity"
round: 2
---

# Critical Review: 2026-11-19-e2e-host-parity

> **Review Mode:** plan
> **Verdict:** approved

## Scope

Complete rolling round-2 review of the working implementation plan, task table and plan-local checks, against the Session 97 grouping, D-1213/D-1214, cited product and test code, Session 96's remote-run contract and named planning receipts. Applied PR-1 through PR-9 and the Materiality Gate. Claude Code (Anthropic) authored the plan; Codex is the independent reviewer.

The original Findings table is preserved verbatim as round-1 history. Its open F1 is closed by the round-2 Prior Pass Summary below; `findings_count: 0` is the current open count. Q1–Q7 state the current assessment. No repository file was edited, staged or committed. All writes were under `C:/Temp/av-kit`; no product suite, package manager, Electron launch, network request or remote command ran. The disclosed sandbox-only untracked settings file was not opened.

## Intent Anchor

the full Electron E2E suite passes on the second Windows host (the mini-air) through `tools/e2e_remote.py run <commit>` at this session's final tree, with 232 tests, 232 expected, the two clipboard specs skipped by their tracked `skip` entries, and `tools/e2e_host/known-failures.json` holding no `known` entry; the four entries it holds now are shown passing in that run's `known_now_passing`. Two causes are fixed, each after a receipt names the side that moves with numbers from both hosts, and each with its own Red: 1. **The capture text plate.** The preview's text plate (`textBackgroundBox` in `ui/src/renderer/src/features/capture/capture-text-metrics.ts`) is 2 px narrower on the right than the plate the bake paints. The bake is the reference (D-1242): `adapter.text_plate_box` returns Pillow's inclusive `(l, t, r, b)` and `_apply_text` fills `draw.rectangle` over it, so the painted plate is `r - l + 1` wide; the preview drops that pixel and scales a 16 px glyph table linearly, where FreeType rounds each size's extents and advances itself. The preview now computes the box from a Segoe UI glyph and kerning table in font units with FreeType's 26.6 rounding and Pillow's basic-layout kerning (D-1243, `PLATE_UNITS`) and returns the painted rectangle (`PREVIEW_FOLLOWS_BAKE`). A Pillow fixture of 2,488 painted boxes pins it; the measured residual (1,702 of 2,448 breadth cases exact, 5 more than 1 px off on a side, worst 2) is pinned as a threshold and registered as a low issue (D-1244). The three fidelity specs run at a device scale of 1 on every host (`FIDELITY_FRAME`, D-1245), so the dev PC, at a scale of 2, measures what the mini-air measures. 2. **The hover colour.** The mini-air has no pointing device, so Chromium reports `hover: none`, and Tailwind v4 puts every `hover:` style inside `@media (hover: hover)`; `settings.test.ts` AC-126.8 hovers a button and waits for a colour that cannot apply there. The spec now launches with a Blink setting that states a mouse-capable device (`HOVER_CAPABLE`, D-1246), checks that the media query matches before it hovers, and no other spec changes.

Executing the revised plan would deliver this intent. Approval is for the plan; implementation and the final-host run remain to be performed and independently reviewed.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | control-defeat | **PINS_NAMED permits an unnamed early return that defeats HOVER_CAPABLE.** `mechanism: task-row-completion-predicate`. `settings.test.ts` uses `inserts=True`; `check()` accepts every inserted line under that flag. The scratch probe added a hover-none guard that closes the app and returns before the new precondition. It returned `checker_problems=[]`, with the capable flag, launch count, precondition ordering and colour assertion still present. If the mini-air ignores the setting, this callback succeeds without the hover assertion, allowing 232 expected and a passing known entry. A row-4 insertion is subsequently frozen by the row-5 hash, so later hash checks do not detect the omission. Violates **AC-161.7**, and defeats the proof required by **AC-161.9/AC-161.11**. Confidence: High. Subject: committable-tooling. | `docs/execution/plans/2026-11-19-e2e-host-parity/diff-check.py:341`; permissive settings rule at `:208`; promised contract in `implementation-plan.md:119` | Restrict insertions to the named hunks at their named locations, reject unmatched insertions, and add this early-return mutation as a failing negative fixture alongside a passing intended-edit fixture. | open |

## Q1. Goal and coverage

Accepted: rows 0–1 establish unchanged baselines and diagnose both causes before tracked edits; row 2 registers MEU-161; rows 3–7 require separate assertion Reds and Greens. Rows 9–10 require KNOWN_EMPTY, the final runtime snapshot, 232 tests/232 expected, both clipboard exclusions, and the four formerly known tests passing in a second summary of that same report. Row 11 resolves both issues and registers the residual through triage tools. H1-2 requires the full dev-PC suite. AC-161.1–15 cover those outcomes (`implementation-plan.md:337`; `task.md:49`).

F1 no longer prevents that proof. The S12 hover fallback remains a partial outcome for the coordinator: keeping a known hover entry cannot satisfy this loop's registered goal or its normal row-10/gate predicates. No new blocker.

## Q2. Diagnosis and direction

Accepted: both mini-air reports show preview right 49 against bake right 51, or 30 against 32 painted columns. The native dev-PC gap is [1,1,1,1]. At scale 1, the width-30 probe reproduces [0,0,2,0] at all three origins; width 32 gives zero. Both font receipts record the same SHA-256, `704eada12961a27fd271f7d3b09e2066520e758390c1776744eff430fee30f6e`.

`adapter.py:223` returns the bbox and `adapter.py:1124` paints its inclusive edges. PREVIEW_FOLLOWS_BAKE serves the retained PNG. Row 1 requires the numerical diagnosis, unchanged baseline hashes and the exact moving-side conclusion; S5 stops execution if a different cause appears (`task.md:51`). No competing measured cause established.

## Q3. Plate model, fixture and consumers

Accepted: PLATE_UNITS includes extent/advance rounding, BASIC-layout kerning, ascent and multiline pitch. A fresh independent arithmetic transcription against `adapter.text_plate_box` reproduced 2,448 breadth cases / 1,702 exact / five over 1 px / worst 2; 40 matrix cases / 36 exact / worst 1; 95 glyphs and 372 kerning pairs. The fidelity boxes are [20,42,32,24] and [20,28,32,106]. This corroborates the measured thresholds rather than merely quoting the planner's totals.

`plate-fixture.py:95` calls the bake directly, independently of the preview arithmetic. The named pins preserve hit-test and transform premises; the old geometry fixture and bake remain unchanged. Non-ASCII fallback, other fonts/layout builds and the measured residual remain disclosed limits. This does not prove universal exact parity. The nonblocking registration-prose correction below should keep those limits accurately described.

## Q4. Fidelity frame and hover

Accepted: FIDELITY_FRAME exposes this geometric defect with the existing 1 px expectations unchanged. The supplied probe also shows width 32 passing at the sampled native scale-2 origins. It does not claim exhaustive native-HiDPI raster coverage (`implementation-plan.md:226`).

HOVER_CAPABLE exercises the product's existing media-gated hover style. The actual AC-126.8 scratch receipt passes natively and fails under hover-none at the expected colour assertion, receiving rgb(21,94,117); the capable probe reports hover true and rgb(22,78,99). The revised precondition is an unconditional `expect(...).toBe(true)`, and AC-161.9 rejects the demonstrated return/skip route (`implementation-plan.md:238`; `:265`). No product hover rule is weakened.

## Q5. Test pins and enforcement

Accepted: the fresh unit/E2E search corroborates the named direct metric values, SVG dimensions, multiline oracle and interaction points, including expert H1's rendered pins. The changed expectations remain exact; replacing the duplicated old line-union model with the independent Pillow oracle improves the evidence. AC-101.6's y=4 setup keeps its southeast plate corner at (8,8).

The revised checker builds the expected file from the row-0 bytes and named rules (`diff-check.py:335`), collapses only explicitly named new/replaced blocks (`:403`), then requires equality (`:426`). The full intended settings hunk passes; the same early-return guard added to it fails. Missing/moved preconditions, a skip, unnamed insertions and a CRLF flip are rejected in the 34-case selftest. New code inside named blocks is deliberately admitted and depends on its assertion Red, frozen hash and execution review; the selftest explicitly demonstrates that limit (`:616`). F1 is fixed; no deeper variant is being made into another blocker.

## Q6. Snapshot and mini-air run

Accepted by source and the supplied snapshot selftest: SNAPSHOT_NO_REF uses a temporary index and commit-tree, with GIT_OPTIONAL_LOCKS=0; guards compare the real index, refs, HEAD and status. Verify checks every named blob, scope completeness and unchanged parent. Row 10 lists all fourteen changed runtime/test/list paths; later register/closeout edits are outside that runtime scope (`snapshot-commit.py:118`; `:172`; `task.md:63`).

The unchanged remote tool archives that commit and validates spec membership/report counts. The second summary uses the original known list while its issues remain open; it is necessary because an empty list cannot name known_now_passing entries (`tools/e2e_remote.py:793`). S10 waits for contention, S11 records operational refusals, S12 stops non-hover failures, and S13 permits one run tied to changed final files. No host configuration change or retry-until-green path is authorized. No live host verification is claimed here.

## Q7. Reds and final gate

Accepted: the hover has its real-spec hover-none reproduction plus the static-contract Red; the plate has the three existing fidelity failures under scale 1 and its numerical unit Reds. Rows 3, 5 and 6 freeze the test files before Green. The named pin movements are source-backed by D-1255; no other moved assertion was identified.

The gate schedules typecheck, ESLint, full Vitest and pytest, ruff, generated-fixture/table checks, touched and full Electron E2E, line endings, home/host scans and register renders. PowerShell execution clears ELECTRON_RUN_AS_NODE and builds required outputs. Future copied helpers, diagnosis.py and session-gate.ps1 are explicitly created before use, rather than claimed to exist already. MEU registration uses the register model/renderer and issue changes use triage tools. No new delivery defect established.

## Checklist Results

Manual procedure: read the complete revised plan/task, inspect the corrected checker and relevant generators, launcher, capture producer/consumers and remote summary path; compare the named receipts and grouping/issue decisions; map AC-161.1–15 to their rows. Observer: codex-independent-reviewer. Exit: null. These are plan-readiness checks, not completed product-gate results.

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Revised rows 3–7 and the plan agree on named hunks, hard precondition, Reds, hashes and Green. |
| PR-2 Not started | pass | Implementation rows remain unchecked; fresh tracked diff exits 0. Only the plan folder and disclosed ignore artifact appear untracked. |
| PR-3 Task contracts | pass | Owners, deliverables, dependencies and commands are present; future helpers precede their callers. |
| PR-4 Validation realism | pass | Full intended edit passes, original bypass is rejected; numerical and remote predicates bind concrete evidence. |
| PR-5 Source-backed planning | pass | Named ACs, grouping, triage and handed decisions support the behavior; no additional uncovered M-list hit established. |
| PR-6 Corrections readiness | pass | F1's correction is identified in the round-1 note and supported by the named selftest/probe receipts and fresh reproduction. Paperwork form is outside the explicit review scope. |
| PR-7 Scope discipline | pass | The bake, host/tool settings, clipboard exclusions and other-font limits follow the supplied decisions. |
| PR-8 Reachability/negative oracle | pass | F1's negative fixture now fails; plate oracle and final-tree snapshot have production producers and negative checks. |
| PR-9 Single-statement contracts | pass | Named contracts and AC-161.5 clearly govern acceptance; stale registration prose is inferable and nonblocking. |
| AV-1–AV-6, applicable plan checks | pass | Separate assertion Reds, frozen tests, no unnamed bypass, explicit exclusions, source-backed criteria and no unplanned completed stubs. |

### Fresh reviewer probes

Every Python command below ran with PYTHONDONTWRITEBYTECODE=1; git reads used GIT_OPTIONAL_LOCKS=0. Receipts are under C:/Temp/av-kit. The original probe's exit 1 is the expected rejection of its old false-pass assertion, not a successful product test.

| Probe | Actual command | Exit | Decisive observation |
|---|---|---|---|
| Corrected checker | `rtk proxy python docs/execution/plans/2026-11-19-e2e-host-parity/diff-check.py --selftest` | 0 | selftest: PASS (34 cases); intended edits pass, early-return mutant fails. |
| Full-hunk companion | `rtk proxy python C:/Temp/av-kit/e2e-host-parity/ehp-pin-probe-intended.py` | 0 | intended edit: diff-check pass; static read pass. Early-return mutant: both fail. |
| Original round-1 probe | `rtk proxy python C:/Temp/av-kit/ehp-pin-probe.py` | 1 | Unnamed guard lines are reported; the stale `assert not result.problems` raises AssertionError. Its nominal edit also lacks the now-required full named hunk. |
| Model arithmetic | `rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/ehp-model-probe.py` | 0 | breadth 2448 / exact 1702 / over_1px 5 / worst 2; matrix 40 / exact 36 / worst 1; 95 glyphs, 372 pairs. |
| Pin census | `rtk proxy rg -n 'textBackgroundBox\|text-bg-plate\|width: 15, height: 12\|width: 30, height: 24\|87\.5\|150, 75, 175, 100\|text_plates' ui/tests/unit ui/tests/e2e` | 0 | Direct, SVG-reading, multiline and interaction pins match the named set; unrelated fit-map/AC-87.5 hits excluded by inspection. |
| Tracked-tree preservation | `rtk proxy git diff --exit-code HEAD` | 0 | No tracked diff; only the disclosed global-ignore permission warning. |

### Nonblocking correction note

`meu-register.py:71` still promises agreement within 1 px on any host/device scale, and `:157` still describes 1,904 cases/14 texts. Align that generated prose with the authoritative AC-161.5: 2,448 breadth cases/18 texts and its measured limits, plus the separate 40-case matrix. This is a Low wording/count correction: the actual fixture, model, test thresholds and acceptance rows are unambiguous and remain intact. It does not require another plan-review round.

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |

### Confirmed Fixes

- PINS_NAMED no longer uses unrestricted inserts. Exact Insert hunks and named block boundaries are checked against a file reconstructed from its row-0 copy (`diff-check.py:335`, `:426`).
- HOVER_CAPABLE's hard assertion and the no-return/skip static contract are explicit in the plan and task rows (`implementation-plan.md:240`, `:265`; `task.md:53`).
- Fresh selftest and full-hunk probe prove both intended acceptance and rejection of the original bypass. The unchanged old probe now exits 1 because acceptance is no longer reproduced.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No new findings. The nonblocking prose note above is carried in the verdict summary, as requested.

### Recheck evidence

```json
{"schema_version": "evidence.v1", "check_id": "ehp-r2-diff-selftest", "command": "rtk proxy python docs/execution/plans/2026-11-19-e2e-host-parity/diff-check.py --selftest", "cwd": "P:/av-kit", "scope": "round-2 plan review; no product-suite execution", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2c41c70 plus the reviewed untracked Session 97 plan; current plan-local scripts and in-memory source copies", "output": "selftest: PASS (34 cases); intended edits pass; round 1 early-return mutant fails; unnamed additions, missing/moved precondition, test.skip and line-ending change fail; a line inside a named new block passes as disclosed.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehp-r2-full-hunk", "command": "rtk proxy python C:/Temp/av-kit/e2e-host-parity/ehp-pin-probe-intended.py", "cwd": "P:/av-kit", "scope": "round-2 plan review; no product-suite execution", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2c41c70 plus the reviewed untracked Session 97 plan; current plan-local scripts and in-memory source copies", "output": "intended edit: diff-check pass; static read pass. early-return mutant: diff-check fail; static read fail. No repository file written. PASS", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehp-r2-original-probe", "command": "rtk proxy python C:/Temp/av-kit/ehp-pin-probe.py", "cwd": "P:/av-kit", "scope": "round-2 plan review; no product-suite execution", "phase": "plan-review", "exit_code": 1, "result": "pass", "tested_state": "HEAD 2c41c70 plus the reviewed untracked Session 97 plan; current plan-local scripts and in-memory source copies", "output": "Unnamed guard lines are rejected. The original assert not result.problems raises AssertionError. Its nominal edit omits the full named HOVER_CAPABLE insertion hunk; the full-hunk companion supplies the positive case.", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "ehp-r2-model", "command": "rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/ehp-model-probe.py", "cwd": "P:/av-kit", "scope": "round-2 plan review; no product-suite execution", "phase": "plan-review", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2c41c70 plus the reviewed untracked Session 97 plan; current plan-local scripts and in-memory source copies", "output": "breadth cases 2448 exact 1702 over_1px 5 worst 2; matrix cases 40 exact 36 over_1px 0 worst 1; glyphs 95 kerning_pairs 372; fidelity [20,42,32,24] [20,28,32,106].", "fresh": true}
```

## Verdict

**approved** — F1 is fixed and no new evidence-backed High/Critical defect remains. The revised plan would deliver the registered intent when its normal acceptance rows pass. The numerical residual, alternate-font/layout limits and S12 partial-outcome boundary remain disclosed; this approval certifies no unperformed execution result. Coordinator: save this complete rolling report to the canonical review path and record the matching round-2 verdict. No repository correction was made by this reviewer.
