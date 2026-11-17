---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "csd-plan-2026-11-15-convert-settings-drafts"
round: 2
---

# Critical Review: 2026-11-15-convert-settings-drafts

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Intent Anchor

an open capture settings edit keeps only what the user changed, follows every other saved value and saves only the changed fields; a Convert Advanced edit (CQ, scale, audio) or preset pick survives settings arriving or changing; and a Convert queue card shows a Cut's in and out points as time codes, a waiting job's current place in the queue, and, for a Cut, the encoder it really runs.

Executing the revised plan would deliver that objective. Both round-1 findings are fixed in the plan; there are no new findings. This is approval of an unstarted plan, not certification of implemented runtime behavior.

## Scope

Read the whole working-tree plan and task, the original report, the six product surfaces, cited test/helpers, relevant API/adapter/repository sources, Session 81's grouping and five issues, the 06/08/10 homes, HDP sections 4a/5/5a/6 and D-970's expert receipt. Applied PR-1–PR-9 and the Materiality Gate to delivery substance, as requested. Claude Code/Anthropic authored the plan; Codex is the independent reviewer and did not author it.

Only `implementation-plan.md` and `task.md` exist in the target folder. `baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py` and `session-gate.ps1` are explicitly scheduled creations in rows 0/H1-2. Their absence is not an undeclared missing deliverable. Inspected the specified source scripts and gate precedent; future adaptations must still meet the plan's stated contract.

Reviewed SHA-256: implementation plan `71164460ee1bd4356cba5ca4149e055bbbf119021d84bf06cb22676caf724e5c`; task `6941d82c1292806dbf4b527bc6421b8013f2c671e18d35d4b3b38d9ae4cbb27f`. No repository files were written. No pytest, Vitest, Electron, package operation or network request ran. Reviewer probes and byte-copy fixtures were written only under `C:/Temp/av-kit`; the coordinator installs the canonical report.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| R1-F1 | High | yes | behavior | `CAPTURE_DRAFT_CHANGED_ONLY` retains a key after the user reverts it to the saved value. With saved hotkey F2, edit inbox to X, hotkey to F9, then back to F2. The specified merge still holds `{ inbox_dir: X, hotkey: F2 }`. If another client saves F3 and the query refetches, the form still shows F2 and `CAPTURE_SAVE_CHANGED_ONLY` PUTs both inbox and F2, overwriting F3. This preserves the stale-baseline defect for a reverted field. AC-151.3 checks no PUT only before that later refetch; AC-151.1/AC-151.2 never test a reverted sibling. Violates AC-151's changed-only/follow-other-saved-values contract (06:1652). Confidence: High. | `docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md:109`; `:110`; `:167` | Remove a capture draft key when a patch returns it to the current saved value. Extend AC-151.3 with the reverted-hotkey/refetch/Save sequence while inbox remains dirty; require F3 in the form and exactly `{ inbox_dir: X }` in the PUT. Retain the intentional Convert preset/field-choice semantics. | open |
| R1-F2 | High | yes | behavior | Row 0/S2 compares every scoped existing product/test file, including read-only E2E inputs, with HEAD and stops on a difference. Yet line 250 expressly expects Sessions 75/78 to change `capture-inbox.test.ts` before this session, and the supplied execution order permits those changes to remain uncommitted. Thus a valid start state stops before either MEU's Red/Green work; the planned AC-151.13 and AC-152.12 gates cannot be reached without an extra human rebaseline or preceding commits. This contradicts D-971 and the required content-bound baseline. Session 75's source gate explicitly identifies the appended AC-146.19 in this file; Session 78's baseline also inventories both E2E files and capture unit files. Confidence: High. | `docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md:284`; `:326`; `docs/execution/plans/2026-11-15-convert-settings-drafts/task.md:46` | Capture approved predecessor contents at row 0, including read-only tests, and compare subsequent state against those hashes/copies. For overlapping edited files, inspect the current relevant code/test sections for incompatible changes; do not make equality to HEAD a prerequisite. Update S2 and row 0 consistently, retaining S4's protection against changes after baseline capture. | open |

## Q1 — Goal and coverage

Accepted: every goal clause has an AC and a producer reached by a task row. Rows 1–2 implement `CAPTURE_DRAFT_CHANGED_ONLY` and `CAPTURE_SAVE_CHANGED_ONLY` (AC-151.1–AC-151.9), plus `CONVERT_FIELD_CHOICE` and `CONVERT_PRESET_PICK` (AC-151.10–AC-151.13). Rows 3–4 implement `CONVERT_TIMECODE`, `CUT_SEGMENT_TIMECODE`, `QUEUE_ROW_NUMBER`, `WAITING_POSITION` and `CUT_NO_GPU_ENCODER` (AC-152.1–AC-152.12).

The prior missing reverted-field sequence now appears explicitly in AC-151.3 (`implementation-plan.md:167`). New test files, production page wiring, existing regression guards, the fresh session gate and Mat's human check cover the required observable outcomes. No remaining delivery gap was found.

## Q2 — MEU-151 draft and Convert state

Accepted: the changed contract (`implementation-plan.md:109–112,167,369–391`) removes every draft key equal to the latest baseline when patching and collapses an empty draft to null. Modeling inbox X, hotkey F9, hotkey F2, then refetched F3 gives `form.hotkey = F3` and exactly `{ inbox_dir: 'X' }` for Save. The partial draft keeps late-GET and other untouched leaves live. Save validates the full merged form first, filters only changed draft leaves, and skips an empty PUT. The API accepts partial input: `routes/settings.py:39–42` uses `exclude_unset=True` and updates supplied leaves; the seven-leaf renderer validation boundary stays intact. Draft clearing follows success as today.

Accepted: Convert choices intentionally differ from persisted capture deltas. Choosing a value equal to the preset remains a next-Add choice; it cannot write back stale settings. Nullish fallback preserves scale 0. A preset selection clears CQ/scale/audio choices and fixes the selected preset against later saved defaults. A model using all five actual presets passed 100 transitions, including equal-value picks. The deleted effect (`ConvertPage.tsx:270–280`) only resets these four values; the snapshot, settings hook, encoder choice and other effects remain. Derived values feed both Add and command snapshots. The named moved assertions retain their existing titles (plan `:153–155`, task row 1); M-7 scope is explicit. No new MEU-151 finding.

## Q3 — MEU-152 queue and encoder behavior

Accepted: the service has one worker, pauses between jobs, and selects the first Pending job from `list_ordered()` (`conversion.py:458–496`). The repository orders by `queue_position` (`repositories.py:399–403`); the page uses the received array without sorting. Counting preceding Pending rows therefore matches run order after moves, removals, finishes and a pause; non-Pending cards do not count as waiting. The corner remains a contiguous 1-based displayed row. `Waiting - next` and `Waiting - N in line` distinguish waiting rank from that corner and implement D-970's expert-adjusted interpretation of 08:646 and 10:87.

Accepted: absent `waitingPosition` preserves the existing shared-card text exactly. The fixture is read-only and checked against its row-0 hash in task row 4 and `scope-paths`; independently measured SHA-256 remains `87ea3fa43666886902bc623cc5d5701cfaa3cce9f688d0cc8bc86c23c1ba649a`.

Accepted: Fast Copy and missing copy mode resolve to no stored encoder; Reencode resolves to `libx265`, without GPU detection/resolution. This matches the adapter's `-c copy` / `libx265` paths (`adapter.py:771–783`) and the service's missing-mode fallback (`conversion.py:589`). A retry overwrites the legacy label at dispatch. The nullable stored/REST/MCP field and adapter input shape remain unchanged; Compress/Extract are guarded by existing tests. No new MEU-152 finding.

## Q4 — Tests and gate

Accepted as test design: AC-151.3 now proves the exact prior counterexample. Red rows require each changed behavior to fail by assertion and separately preserve the child exit. Already-passing guards are excluded from required-failure selections; moved pins are changed in Red, with Green expectations immutable. Mutable GET answers, query invalidation and awaited observable settlement can exercise the stated late/refetch sequences without timing guesses. Existing helper setup is reusable; broadening a fixture's literal preset type for the new helper is a setup change, not an assertion change.

The commands run in pwsh through `npm --prefix ui run test`; npm runs the package script with effective cwd `ui`, equivalent here to `Set-Location ui`. Python runs use `uv run pytest`. The planned gate includes Python/Vitest targeted and full runs, types, lint, formatting, UI compilation and both relevant real-Electron runs with `ELECTRON_RUN_AS_NODE` cleared (`implementation-plan.md:325–342`, task H1-2). The targeted rows do not excuse baseline failures. No product test result is claimed by this review.

## Q5 — Order, safety, registers and human check

Accepted: MEU-151 precedes MEU-152. Row 0 now binds predecessor state to path-scoped hashes and byte copies; `baseline-predecessor.diff` is diagnostic, not a HEAD-equality gate. S2 and S4 preserve that distinction (`implementation-plan.md:280–307,349–351`; `task.md:42,46`). An uncommitted predecessor E2E edit can enter the baseline if its required anchors and line endings hold. Baseline copies must use raw bytes; the independent copy probe preserved all 15 anchored files, including every CRLF file and `convert-controls.ts`'s eight bare-LF lines. Subsequent comparisons use row-0 content; no clean-tree or preceding-commit requirement is imposed by these checks.

Accepted: H1-4 compares the union of baseline/current API and MCP path sets and hashes (`task.md:63`), detecting edits, additions and deletions. It measures Session 81's delta, allowing earlier uncommitted work. It supplies a valid skip basis for this session because the core change keeps the existing field shape; it does not certify earlier sessions' changes. Row 7 binds issue writes to the row-0 register hash through the resolver's exclusive Windows handle and `tools/issue_triage` model; status/render writes use `tools/meu_status.py`. Other sessions' content remains protected by S4 and execution review against the copies.

HC-1–HC-4 (`task.md:54`) are concrete pass/fail observations for timecodes, current waiting rank after finish/remove, NVIDIA Fast Copy labeling and settings persistence across pages. The M-10 stop remains required. Existing authorization allows execution after approval; older prose asking for another execution message does not revoke it. This session still ends uncommitted with a commit-message draft.

## Recheck (round 2)

**Prior Pass Summary**

| Finding | Prior Status | Recheck Result |
|---|---|---|
| R1-F1 | open | fixed |
| R1-F2 | open | fixed |

### Confirmed Fixes

- R1-F1: `implementation-plan.md:109,167,369–377` now removes reverted keys and requires the precise refetch/Save counterexample. Task rows 1–2 consume that contract. Convert's retained equal-value choice is separately justified at `:111,391` and matches its next-Add semantics.
- R1-F2: `implementation-plan.md:282–287,349,444–452` and `task.md:42,46,52,63,69` replace HEAD equality with row-0 hashes/copies, line-ending metadata, skip snapshots and the content-bound execution-review delta. The remaining `git diff HEAD` produces the predecessor diagnostic only. S4 continues to detect content drift after capture.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No new findings.

### New-mechanism probes and limits

| Surface | Probe / trace | Result |
|---|---|---|
| Anchor strings | All 39 exact plan anchors exist. A modeled `convertMetaSegments` mutation returning an empty array retains its anchors but contradicts AC-152.3's exact segment assertion, which row 4 and the targeted gate run without baseline excuses. | Accepted as compatibility landmarks with behavioral tests behind them; anchors alone are not semantic approval. No materially missing deliverable was shown to pass the full plan. |
| Baseline line endings | Copied raw bytes of all 15 anchored inputs into reviewer scratch and compared exact bytes. All copies match; pure CRLF files stay CRLF and the mixed helper has exactly 8 bare-LF lines. | pass |
| Skip hashes | Applied H1-4's union-of-keys/content comparison to safe fixtures with an edit, an added file and a deleted file. All three produce nonempty differences; unchanged input produces none. | pass |
| Convert pick rule | Applied the stated null-choice derivation to all five real presets; 100 transitions preserve field picks, including a pick equal to the old preset and scale 0, while a preset pick resets field choices. | pass |

The scripts being created during execution are still implementation obligations. Their claimed behavior is reviewed as specified design, not as already executed code. The planning-only anchor probe compares HEAD hashes to demonstrate checkout normalization; it neither implements row 0 nor rejects predecessor differences. Its looser fixture needle was tightened to the plan's full `Waiting - position 1 in queue` string in the independent probe and passed. No new AC or decision is needed.

### Round-2 verdict

`approved` — both prior defects are fixed within the existing AC families and decisions; no new evidence-backed High/Critical failure was found.

## Checklist Results

Manual observer: `codex-independent-reviewer`. Results judge plan adequacy; unexecuted product suites remain execution obligations.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read whole plan/task; compare rows 0–8/H1/H2 and revised contracts | null | Same scope, dependency order and content-bound baseline design |
| PR-2 Not started | pass | Inspect target folder and task status cells | null | Only the two plan documents exist; work rows remain unchecked |
| PR-3 Task contracts | pass | Read task table owners/deliverables/validation/dependencies | null | All work rows specify their outputs and checks |
| PR-4 Validation realism | pass | Trace revised AC-151.3, row-0 preconditions, rows 1–4 and H1-4 | null | Prior counterexample is required; permitted predecessor content is accepted; target checks remain unexcused |
| PR-5 Source-backed planning | pass | Compare D-966–D-972 against 06/08/10, actual hooks/API/adapter and HDP | null | Rules serve the goal; D-970's handed-over M-5 has no additional mandatory-human hit |
| PR-6 Corrections and review readiness | pass | Trace both prior ids through changed plan/task rows and this report's recheck | null | Both concrete failures are resolved; two MEU handoffs and independent execution review remain scheduled |
| PR-7 Scope discipline | pass | Compare exclusions to homes and source request | null | Other queues, stored renumbering, converter Save body and old-row migration have valid scope bases |
| PR-8 Reachability/negative oracle | pass | Trace hook/page/PUT, helper/card and service/adapter production chains; inspect required negatives | null | Every goal observable has a producer and failing negative case; anchors are backed by behavioral checks |
| PR-9 Contract consistency | pass | Compare named contracts, ACs, decisions and task references | null | No materially divergent live behavior; D-966/D-967 distinguish deltas from next-Add picks explicitly |
| Independent plan probes | pass | `rtk proxy python C:/Temp/av-kit/csd-round2-probes.py` with `PYTHONDONTWRITEBYTECODE=1` | 0 | Reverted-field sequence, 100 Convert transitions, 39 anchors, 15 byte copies, skip edit/add/delete negatives and referenced tools pass |
| Product execution | n/a | Not run under review restrictions | null | No product-suite or package command ran |

```json
{"schema_version":"evidence.v1","check_id":"csd-round2-plan-probes","command":"rtk proxy python C:/Temp/av-kit/csd-round2-probes.py","cwd":"P:/av-kit","scope":"revised draft/pick models, exact anchors, byte-copy/EOL checks, skip comparison negatives and invoked-tool existence","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"plan=71164460ee1bd4356cba5ca4149e055bbbf119021d84bf06cb22676caf724e5c;task=6941d82c1292806dbf4b527bc6421b8013f2c671e18d35d4b3b38d9ae4cbb27f","output":"R1-F1 sequence: draft={inbox_dir:X}; refetch form.hotkey=F3; PUT={inbox_dir:X}. Convert choice model: 100 preset transitions pass including equal-value picks and scale=0. All 39 anchors present, 15 byte copies identical, mixed helper has 8 bare LF. H1-4 model refuses edit/addition/deletion. Three new tests absent; six invoked tools exist. queue-slot-baseline SHA-256 87ea3fa43666886902bc623cc5d5701cfaa3cce9f688d0cc8bc86c23c1ba649a. Models only; no product suites.","fresh":true}
```

## Report validation

The read-only report parser recognized `review_mode=plan; round 2 of 3; verdict=approved; open findings=0`. The JSON verdict also validates against the repository's `review-verdict.schema.v2.json`. Completion-preflight was applied to this review artifact only: the product task remains intentionally unstarted and was not edited.

```json
{"schema_version":"evidence.v1","check_id":"csd-round2-report-state","command":"rtk proxy python tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/csd-plan-review-round-2.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-15-convert-settings-drafts/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/convert-settings-drafts/review/round2-state.json","cwd":"P:/av-kit","scope":"rolling report target, round and open findings","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"plan=71164460ee1bd4356cba5ca4149e055bbbf119021d84bf06cb22676caf724e5c;task=6941d82c1292806dbf4b527bc6421b8013f2c671e18d35d4b3b38d9ae4cbb27f","output":"OK: review_mode=plan; round 2 of 3; verdict=approved; open findings=0","fresh":true}
```

## Verdict

`approved` for ledger round 2. Current open findings: 0. The original Findings table is retained as historical evidence; the round-2 Prior Pass Summary closes both rows. Proceed with authorized execution in session order, including the planned human check and independent execution review. No commit or push is authorized by this verdict.

🕐 Completed: 2026-11-15 15:22 (EST)
