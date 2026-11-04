---
date: 2026-09-03
review_mode: plan
target_plan: docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md
verdict: changes_required
round: 2
findings_count: 0
template_version: "2.1"
requested_verbosity: standard
agent: gpt-5.6-sol (Codex independent reviewer)
---

# P10 Queue Card DnD — Plan Critical Review, Round 1

## Intent Anchor

MEU-49 must add an accessible dnd-kit pointer/touch/keyboard reorder path to the shared `QueueList` without degrading the existing Alt+Arrow and menu alternatives, without confusing row drag with the surrounding HTML5 file-drop zone, and without changing the API's absolute-permutation wire contract. The plan is unstarted: no MEU-49 implementation symbols or dependencies are present in the current source tree.

## Findings

| ID | Severity | Rubric | Finding | Evidence | Required correction |
|---|---|---|---|---|---|
| F1 | High | PR-5, PR-8 | `ALT_ARROW_SUPPRESSION_RULE` prevents Alt+Arrow only during the local dnd-kit drag, but it does not serialize absolute-permutation PUTs across keyboard, pointer, menu, or bulk reorder paths. A keyboard PUT can start from order A, a drag PUT can then start from the same stale rendered order A, and the keyboard response can land last and overwrite the drag with another valid absolute permutation. `run()` only tracks busy state; it is not a synchronous mutation lock, and neither reorder callback checks it. | `named-sets.json:100-103`; `implementation-plan.md:177`, `implementation-plan.md:217`, `implementation-plan.md:252`; `task.md:35`, `task.md:38`; `ui/src/renderer/src/features/downloader/DownloaderPage.tsx:293-324`; `ui/src/renderer/src/features/converter/ConvertPage.tsx:354-385`; `ui/src/renderer/src/features/downloader/download-commands.ts:381-412`; `ui/src/renderer/src/features/converter/convert-commands.ts:423-455` | Define one cross-path concurrency policy for every queue permutation mutation. Add a synchronous single-flight/serialization guard or disable all competing reorder entry points until settlement. Add controlled deferred-promise negative tests for both completion orders and for keyboard-versus-drag plus menu/bulk-versus-drag overlap. |
| F2 | High | PR-3, PR-8 | `MOVE_TO_INDEX_CONTRACT` is internally ambiguous: it calls `targetIndex` an index into the array “after removal” while also claiming dnd-kit's `arrayMove` semantics. In the standard sortable pattern the `over.id` index is found in the original item array and becomes the final index supplied to `arrayMove`. For `[A,B,C,D]`, moving `A` over `C` must be pinned as `[B,C,A,D]`; an implementation that removes first can instead produce `[B,A,C,D]`. AC-49.25 merely says the order changes, so both interpretations can pass. | `named-sets.json:60-62`; `implementation-plan.md:141`, `implementation-plan.md:150`, `implementation-plan.md:217`, `implementation-plan.md:285` | State the final-index contract with explicit forward and backward examples and define `targetIndex = items.findIndex(item.id === over.id)` against the pre-move array. Require exact expected permutations in pure-builder unit tests and in the pointer E2E assertion. |
| F3 | High | PR-5, PR-8 | The plan claims PointerSensor covers touch but never specifies `touch-action: none` on the drag handle and has no touch-path validation. Under Pointer Events, cancelling the initiating touch movement with an event listener is not reliable; dnd-kit specifically recommends `touch-action: none` on a dedicated activator in a scrollable list. The planned mouse E2E cannot expose this failure, so touch dragging can scroll or cancel instead of reordering. | `named-sets.json:70-82`; `implementation-plan.md:170-178`, `implementation-plan.md:229`, `implementation-plan.md:285`; `task.md:35`, `task.md:37`; [dnd-kit Pointer Sensor documentation](https://dndkit.com/legacy/api-documentation/sensors/pointer/) | Put `touch-action: none` on the dedicated handle (for example `touch-none`) and assert the DOM/style contract. Add a touch/pointer validation case, or explicitly choose separate mouse and touch sensors with source-backed activation behavior and test that choice. |
| F4 | High | PR-4, PR-8 | The registered Playwright command is not independently runnable from the repository root. `npx --prefix ui playwright test --list` exits 1 after scanning Vitest unit files (`Vitest failed to access its internal state`) and reports zero tests. Running from `ui/` loads the intended config and lists 73 tests in 12 files. As written, the task table cannot prove E2 or AC-49.30. | `implementation-plan.md:411`; `task.md:40`; receipt `C:/Temp/av-kit/review-e2e-list.txt`; corrected receipt `C:/Temp/av-kit/review-e2e-list-ui-cwd.txt` | Change every E2E validation row to enter `ui/` (or pass the explicit Playwright config) while preserving exit status and returning to the prior directory. Make the gate assert both the 73 runtime-test floor and the 67 static `*.test.ts` case floor. |
| F5 | High | PR-4, PR-8 | The Red-phase row unconditionally exits 0 after capturing the test exit code. It neither requires a non-zero result nor proves that the failures are the intended AC-49 failures. A still-green suite, no tests collected, or an unrelated failure can therefore satisfy the plan's TDD checkpoint and later marker scripts. This is a substantive false-pass in the execution contract, not a formatting issue. | `task.md:33`; `task.md:49`; `docs/execution/plans/2026-08-28-p10-queue-card-foundations/task.md:45`; `.agent/docs/emerging-standards.md:619-642` | Add a Red oracle that rejects exit 0, no-test collection, and unrelated failures, and that asserts the expected AC-49 failure signatures from a machine-readable Vitest receipt before implementation begins. Preserve that receipt for FAIL_TO_PASS evidence. |
| F6 | Medium | PR-5 | Three mandatory GUI standards are waived or redefined without a source-backed exception. The plan requires a bare `<button>` although the canonical `Button` already forwards refs and exposes suitable `ghost`/`sm` or icon styling; it says G35 does not apply although drag reorder is state-changing; and it substitutes `fireEvent` for G37's explicit `userEvent.setup()` requirement even though the earlier package freeze has expired and this plan already changes manifests. | `implementation-plan.md:178`, `implementation-plan.md:335-336`, `implementation-plan.md:363`; `task.md:33`, `task.md:35`; `.agent/docs/emerging-standards.md:1132-1137`, `.agent/docs/emerging-standards.md:1149-1154`, `.agent/docs/emerging-standards.md:1212-1217`; `ui/src/renderer/src/components/ui/Button.tsx:37-50`, `ui/src/renderer/src/components/ui/Button.tsx:62-68`; `docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md:594-595` | Use the canonical ref-forwarding `Button`, assign the drag mutation a G35 feedback tier, and use actual Testing Library user-event for interaction tests—or document a canonical/human-approved exception and its bounded follow-up. |
| F7 | Low | PR-3 | The AC table does not supply a negative test for every AC: AC-49.29 contains a dash, and AC-49.25's “negative” only constrains the test driver rather than stating an adverse product outcome. The underlying E2E can still be meaningful, so this is informational and not independently blocking. | `implementation-plan.md:285`, `implementation-plan.md:289` | Give AC-49.25 an exact wrong-order/no-PUT adverse assertion and AC-49.29 a negative outcome such as missing/incomplete pointer-state coverage causing the test to fail. |
| F8 | Low | PR-7, PR-9 | Two carry-forward facts are stale. The live unstarted Vitest baseline is 439, not 438. The plan also says MEU-56/TTS will inherit reorder by adopting `QueueList`, but the registry and matrix assign that adoption dependency to MEU-55/Transcript; MEU-56 adopts the shared progress primitive instead. Neither drift changes MEU-49's implementation scope. | `named-sets.json:211-214`; live receipt `C:/Temp/av-kit/review-baseline-vitest.txt`; `implementation-plan.md:30`; `named-sets.json:68`; `.agent/context/meu-registry.md:149-150`; `.agent/context/meu-status.yaml:1472-1487` | Refresh the Vitest floor to 439 and narrow the inheritance statement to MEU-55 unless separate canonical evidence establishes later TTS adoption. |

## Scope Reviewed

Primary targets:

- `docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md`
- `docs/execution/plans/2026-09-03-p10-queue-card-dnd/task.md`
- `docs/execution/plans/2026-09-03-p10-queue-card-dnd/named-sets.json`
- The three plan-local closeout assertion scripts

The review also checked the cited build-plan/index/registry/status authorities, GUI emerging standards and testing strategy, both predecessor plan folders, the current QueueList/card/page/command implementation, the download/conversion API schemas/routes/services, relevant unit/E2E tests, UI package scripts, and the current worktree state.

## Verification Performed

| Check | Result |
|---|---|
| Plan-local named-set guard | Exact canonical path match; 72 top-level keys; target review handoff did not pre-exist |
| Plan-local assertion script self-tests | All three passed, including their seeded negative fixtures |
| Migration mount-completeness gate | Passed: 178 checks, 0 pending |
| Backend wire contract | Confirmed both reorder schemas inherit `ApiModel(extra="forbid")`; `{id, direction}` is not accepted by the declared models |
| Vitest baseline | 54 files, 439 tests passed; the plan's 438 count is stale |
| Pytest baseline | 509 passed |
| Static E2E case count | 67 `test()`/`it()` cases across ten `*.test.ts` files |
| Playwright runtime list from repository root | Failed with exit 1 and listed 0 tests |
| Playwright runtime list from `ui/` | Passed; 73 tests in 12 files |
| MEU status generated-view check | Passed: 58 MEUs across 12 phases |
| Package compatibility | Current planned versions are mutually compatible: core 6.3.1, sortable 10.0.0, utilities 3.2.2 |
| Unstarted-state sweep | No `@dnd-kit`, `onMoveToIndex`, `buildReorderBodyToIndex`, `queue-card-drag-handle`, or AC-49 implementation artifacts found under current UI/API source and tests |

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Notes |
|---|---|---|
| Acceptance criteria source-backed | Pass | The 30 ACs are anchored to Spec, Local Canon, Research-backed, or explicit plan contracts. |
| Validation commands independently runnable | Fail | The E2E invocation fails from the declared working directory; the Red row is a false-pass. |
| Build/spec audit present | Pass | Relevant MEU-49 build-plan and action-index rows are mapped. |
| H1/H2 closeout rows present | Pass | All expected phases are represented, though their execution oracles need the corrections above. |

### Documentation Review (DR-1 through DR-8)

| Rule | Result | Notes |
|---|---|---|
| DR-1 Current-state accuracy | Partial | Source/API/package-freeze claims are accurate; Vitest and TTS carry-forward claims are stale. |
| DR-2 No implemented work presented as pending | Pass | MEU-49 is genuinely unstarted. |
| DR-3 Cross-document consistency | Partial | MEU-55 inheritance is canonical; the additional MEU-56/TTS statement is unsupported. |
| DR-4 Command validity | Fail | F4 and F5 prevent evidence-producing execution. |
| DR-5 Test/evidence claims | Partial | Pytest and E2E floors are right; Vitest is off by one and the Red oracle is insufficient. |
| DR-6 Governance and standards alignment | Partial | F6 conflicts with mandatory G34/G35/G37 language. |
| DR-7 Numeric baseline accuracy | Fail | 439 Vitest tests currently pass, not 438. |
| DR-8 Completion-state honesty | Pass | The plan correctly presents itself as unstarted. |

### Plan Review (PR-1 through PR-9)

| Rule | Result | Notes |
|---|---|---|
| PR-1 Scope integrity | Pass | MEU-49 is bounded and sequenced before Phase 11. |
| PR-2 Current-state grounding | Pass | Proposed source surfaces match the current implementation. |
| PR-3 Contract completeness | Fail | Forward/backward move-index semantics are not pinned; one AC lacks a negative case. |
| PR-4 Executability | Fail | The E2E gate and Red oracle cannot reliably establish their claimed states. |
| PR-5 Correctness/accessibility/regression control | Fail | Outstanding mutation-race, touch-input, and mandatory GUI-standard issues remain. |
| PR-6 Review/closeout continuity | Pass | Rolling review paths and correction phases are defined. |
| PR-7 Supersession | Pass with Low correction | Narrowing `/dnd-kit|react-virtual/` to `/react-virtual/` is a legitimate dependency-guard update; the canon clause and action index correctly remain unchanged. Baseline prose needs refresh. |
| PR-8 Anti-false-pass | Fail | F1, F4, and F5 admit stale writes or evidence gates that can succeed without proving the intended behavior. |
| PR-9 Machine-readable carry-forward | Pass with Low correction | `named-sets.json` is well-formed with 72 keys, but contains the stale baseline/TTS facts in F8. |

## Open Questions and Recommendations

- **OQ-3:** Agree with the plan. Do not promote the migration-specific `assert-mount-completeness.ps1` into `.agent/docs/commands.md`. Its hard-coded `downloader`, `convert`, and `all` scopes resolve Phase 10 MEU names (`docs/execution/plans/2026-09-02-p10-queue-card-migration/assert-mount-completeness.ps1:522-528`), so it is appropriate as a one-time carry-forward check and would become a misleading recurring gate after later renames.
- **OQ-4:** Acceptable as written. Do not pre-apply `"use no memo"`. A React Compiler bailout is a safe optimization fallback; capture the build evidence first and add the directive only if the emitted diagnostic demonstrates that it is needed and the plan records the reason.
- The HTML5 file-drop isolation design is sound in principle because dnd-kit's PointerSensor does not emit HTML5 `dragenter`/`dragover` events, and the DnD wrapper/handle are conditional on opt-in. The plan still needs the touch contract in F3.
- The `DND_OPT_IN_RULE` is achievable only through the plan's stated conditional render: when `onMoveToIndex` is undefined, do not mount `DndContext`, sortable rows, handle, or live region. Keep a structural regression assertion for the legacy DOM.
- No backend source change is required. `ReorderIn` and `ConversionReorderIn` inherit the strict extra-field policy and the current services consume an absolute `job_ids` permutation.

## Verdict

**changes_required**

The plan has a strong scope model, a viable opt-in rendering strategy, correct no-backend-change reasoning, and sound preservation of the menu/Alt+Arrow alternatives. It is not safe to execute yet: the absolute-permutation mutation race, ambiguous move index, missing touch-action contract, non-runnable E2E command, and non-enforcing Red checkpoint are substantive defects that can produce regressions or false completion evidence.

## Follow-up Actions

1. Define and test a single-flight or serialization rule across every reorder entry point (F1).
2. Replace the ambiguous post-removal wording with exact final-index examples and exact-order assertions (F2).
3. Add the touch-action/sensor contract and touch validation (F3).
4. Correct the Playwright working directory/config and make both E2E floors executable assertions (F4).
5. Add a fail-closed, AC-specific Red oracle (F5).
6. Resolve G34/G35/G37 explicitly and update the two low-severity AC/baseline/carry-forward details (F6-F8).
7. Re-dispatch the corrected `implementation-plan.md`, `task.md`, and `named-sets.json` together for Round 2.

## Recheck

Not applicable in Round 1. No implementation was reviewed or modified.

---

## Round 2 — Procedural Precondition Review (2026-09-03)

```yaml
date: 2026-09-03
review_mode: plan
target_plan: docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md
verdict: changes_required
round: 2
findings_count: 0
template_version: "2.1"
requested_verbosity: standard
agent: gpt-5.6-sol (Codex independent reviewer)
```

### Intent Anchor

MEU-49 must add accessible pointer/touch/keyboard queue-card reordering without weakening the
existing Alt+Arrow and menu paths, without conflicting with file drop, and without allowing stale
absolute-permutation writes. Before a Round 2 reviewer may adjudicate whether the corrected plan
would deliver that objective, PR-6 requires the correction pass's complete blast-radius evidence.

### Procedural Precondition Failure

The resubmission does not name an untruncated correction blast-radius census receipt, and the
rolling review file contains no correction log that assigns every census hit an `updated` or
`confirmed-consistent` disposition. The plan's correction summary describes F1–F8 and later
self-review changes (`implementation-plan.md:503-557`), but prose summaries are not the required
per-hit audit. The rolling file ended after the Round 1 `Recheck` at line 123 before this section;
no `Corrections Applied` entry was appended.

This is the Round 2+ PR-6 pre-verdict gate, not a severity-rated finding. The review workflow
requires `changes_required` naming this condition alone and forbids substantive review of the
corrected content when the census is missing, truncated, or undispositioned
(`.agent/workflows/plan-critical-review.md:256`, `.agent/workflows/plan-critical-review.md:287-293`).
The correction workflow independently requires both old/new sweeps for every changed value,
semantic-variant declarations, full receipts, and per-hit dispositions
(`.agent/workflows/plan-corrections.md:170-220`).

### Round 1 Finding Disposition

F1–F8 are **not adjudicated in Round 2**. No `CLOSED` / `NOT CLOSED` determination is valid until
the required correction census and disposition log make the correction blast radius auditable.

### Independently Run Verification

| Check | Result | Evidence |
|---|---|---|
| Canonical review target / pre-edit guard | Pass | `C:/Temp/av-kit/round2-preedit-guard.json`: target exactly equals the derived rolling review path and already exists. |
| Correction-census discovery | **Fail** | Unfiltered `rg` receipt `C:/Temp/av-kit/round2-blast-radius-census.txt` contains only implementation-time Red/E2E census references; it names no correction blast-radius receipt, semantic-variant inventory, or per-hit disposition log. |
| Plan correction summary | Present but insufficient | `implementation-plan.md:503-557` contains the F1–F8 summary and self-review narrative, but no receipt path and no `updated` / `confirmed-consistent` mapping for each hit. |
| Rolling correction log | **Fail** | Before this append, the rolling review contained 123 lines and ended with the Round 1 `Recheck`; the required `Corrections Applied` log was absent. Receipt: `C:/Temp/av-kit/round2-handoff-linecount-tail.txt`. |
| `assert-red-phase.ps1` self-test and adversarial review | Not run | Withheld by the mandatory PR-6 pre-verdict stop; no substantive corrected-content review is permitted this round. |
| `assert-plan-gates.ps1` self-test and six live gates | Not run | Withheld by the same mandatory PR-6 pre-verdict stop. |
| F1–F8, empirical claims, cross-file consistency, task dependencies, and command executability | Not evaluated | Deferred without inference because the workflow requires the reviewer to name only the failed procedural precondition. |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1–PR-5 | Not evaluated | Substantive plan review is gated by PR-6 on Round 2+ resubmissions. |
| PR-6 Handoff/corrections readiness | **Fail — pre-verdict gate** | Missing named untruncated census receipt and missing per-hit correction-log dispositions. |
| PR-7–PR-9 | Not evaluated | Substantive plan review is gated by PR-6 on Round 2+ resubmissions. |
| DR-1–DR-8 | Not evaluated | No correction claims were adjudicated after the precondition failure. |

No Critical, High, Medium, or Low findings were adjudicated; `findings_count` is therefore `0`.

### Follow-up Actions

1. Run Step 5c of `/plan-corrections` for every literal, term, count, set, threshold, and predicate
   changed by F1–F8 and the three self-review corrections, including declared semantic variants and
   both old/new fixed-string sweeps over `implementation-plan.md` and `task.md`.
2. Preserve every untruncated receipt under `C:/Temp/av-kit/`, name those receipt paths in the
   resubmission, and append a `Corrections Applied` log to this rolling file assigning every
   `file:line` hit `updated` or `confirmed-consistent`.
3. Re-dispatch the same five-file plan artifact for the next independent review round. That reviewer
   can then run the requested script self-tests/live gates and adjudicate F1–F8 on substance.

### Residual Risk

The corrected design and gates remain unreviewed. No inference is made about whether F1–F8 are
closed, whether the new single-flight design is safe, or whether either plan-local script fails
closed.

### Verdict

`changes_required` — the mandatory Round 2 correction blast-radius census and per-hit disposition
log are absent, so PR-6's procedural exception prevents substantive adjudication in this round.

---

## Corrections Applied — Round 2 blast-radius census (implementor, 2026-09-03)

> Written in response to the Round 2 `changes_required` verdict, which was returned solely on the
> PR-6 procedural precondition: the round-2 resubmission named no untruncated census receipt and
> this rolling file carried no per-hit disposition log. Both now exist. No Round 2 finding was
> disputed — the omission was the implementor's.

### How the census was produced

`/plan-corrections` Step 5c was executed by a new plan-local, self-tested script rather than by an
ad-hoc sweep, so the census is reproducible and its own correctness is testable:

```
pwsh -NoProfile -File docs/execution/plans/2026-09-03-p10-queue-card-dnd/run-correction-census.ps1 -SelfTest
pwsh -NoProfile -File docs/execution/plans/2026-09-03-p10-queue-card-dnd/run-correction-census.ps1
```

Self-test: `PASS: CORRECTION_CENSUS self-test (5 cases)`, exit 0 — receipt
`C:/Temp/av-kit/census-selftest.txt`. Its five cases prove a planted value is found, an absent value
is reported absent, `-F` treats `[0-9]` as literal text (so `AC-49.[0-9]` does **not** match
`AC-49.5`), and a leading-dash value such as `-Census` is swept as a pattern rather than parsed as
an `rg` flag — the defect that produced `rg` exit 2 on the first attempt and is now fixed with
`-e <pattern> -- <paths>`.

Live run: `CENSUS COMPLETE: 45 values, 80 variants, 325 hits`, exit 0 — receipt
`C:/Temp/av-kit/census-run.txt`.

Every sweep is a fixed-string `rg -F -n --no-heading --with-filename -e <value> -- <plan> <task>`
over **both** plan files, in **both** directions (old value and new value), plus hand-declared
semantic variants. Nothing is piped through `head`, `Select-Object -First`, or any other truncator.
`rg` exit 1 (no match) is a valid census result and is recorded; only exit > 1 aborts the run.

### Receipts

- **Index (start here):** `C:/Temp/av-kit/census/census-index.txt` — every sweep's value, direction,
  `rg` exit code, hit count, receipt path, and each hit's full untruncated line.
- **Per-value receipts:** `C:/Temp/av-kit/census/census-<slug>-{old,new,variantN}.txt` — 125 files,
  one per sweep. Directory listing: 126 files (125 receipts + the index).
- **Run receipts:** `C:/Temp/av-kit/census-run.txt`, `C:/Temp/av-kit/census-selftest.txt`.

### Coverage

45 changed values (F1–F8, S1–S6, C1–C3) across `implementation-plan.md` and `task.md`, swept in both
directions, plus 80 declared semantic variants — 125 sweeps, 325 hits.

**Zero-hit NEW values: none.** Every corrected value is present in the tree, so no correction was
claimed in prose but never applied.

### Disposition rule

- A hit on a **NEW** value is `updated` — that line carries the corrected text. Per-value counts and
  receipt names are in the value table below; each receipt enumerates the exact lines.
- A hit on an **OLD** value is a survivor and is dispositioned individually in the table that
  follows. `confirmed-consistent` means the line deliberately *quotes* the superseded value — a
  correction-log row recording what was wrong, or an AC's negative-test clause naming the wrong
  behaviour that must fail. `updated` means the line was changed by this pass.

### Surviving OLD-value hits — per-line disposition (21 hits, 9 values)

| Value | `file:line` | Disposition | Why |
|---|---|---|---|
| `after removal` (F2) | `implementation-plan.md:516` | confirmed-consistent | The F2 correction row quoting the superseded `MOVE_TO_INDEX_CONTRACT` wording. A correction log that cannot name what it corrected is not a log. |
| `npx --prefix ui playwright test` (F4) | `task.md:41` | confirmed-consistent | Row 9 names the forbidden form to say it is forbidden: "…invoked **only** via `E2E_RUN_COMMAND`; `npx --prefix ui playwright test` loads no config, reports 0 tests and exits 1". |
| `npx --prefix ui playwright test` (F4) | `task.md:42` | confirmed-consistent | Row 10's validation column, same prohibition: "per `E2E_RUN_COMMAND` — **never** `npx --prefix ui playwright test`". |
| `npx --prefix ui playwright test` (F4) | `task.md:96` | confirmed-consistent | The task-file note explaining *why* the form fails (it changes package resolution, not the working directory). |
| `npx --prefix ui playwright test` (F4) | `implementation-plan.md:315` | confirmed-consistent | AC-49.30's negative-test clause — the assertion that this invocation form must fail. |
| `npx --prefix ui playwright test` (F4) | `implementation-plan.md:518` | confirmed-consistent | The F4 correction row quoting the defective command. |
| `the order changed` (F7) | `task.md:41` | confirmed-consistent | Row 9 requires the **exact** order `[B,C,A,D]` "never a weaker 'the order changed' check" — the phrase appears as the prohibited weaker assertion. |
| `the order changed` (F7) | `implementation-plan.md:310` | confirmed-consistent | AC-49.25's negative clause: "The assertion is the exact 4-id sequence, not 'the order changed'". |
| `the order changed` (F7) | `implementation-plan.md:516` | confirmed-consistent | The F2 correction row quoting AC-49.25's superseded assertion. |
| `438` (F8) | `implementation-plan.md:522` | confirmed-consistent | The F8 correction row quoting the wrong baseline it replaced. `VITEST_BASELINE_COUNT` is 439 everywhere it is used. |
| `MEU-56` (F8) | `implementation-plan.md:35` | confirmed-consistent | §Goal, already correct: "MEU-56 (TTS) inherits the shared `ProgressBar`, not `QueueList`". |
| `MEU-56` (F8) | `implementation-plan.md:404` | **updated** | **Real residual defect the census caught.** See S4 below. |
| `MEU-56` (F8) | `implementation-plan.md:522` | confirmed-consistent | The F8 correction row quoting the wrong inheritance claim it removed. |
| `MEU-56` (F8) | `implementation-plan.md:569`, `:571`, `:572`, `:573` | confirmed-consistent | The new S4 self-review entry describing the `:402` defect and its fix. |
| `<the VITEST_EXIT from row 3>` (S2) | `implementation-plan.md:542` | confirmed-consistent | The S2 self-review entry quoting the human-substituted placeholder it removed. |
| `-Pattern 'AC-49\.').Count` (S3) | `implementation-plan.md:560` | confirmed-consistent | The S3 self-review entry quoting row 1's false-passing receipt expression. |
| `Drag reorder on the Transcript and TTS queues` (S4) | `implementation-plan.md:570` | confirmed-consistent | The S4 self-review entry quoting the combined Out-of-Scope row it split. |
| `meu-registry.md:149-150` (S4) | `implementation-plan.md:578` | confirmed-consistent | The S4 self-review entry quoting the citation it replaced. |

Every survivor is a deliberate quotation inside a correction log or a negative-test clause, except
`implementation-plan.md:404`, which was a real contradiction and is fixed.

### S4 — the defect the census found

The census earned its cost on its first run. F8 (Round 1, Low) narrowed the reorder-inheritance claim
from "MEU-55 and MEU-56" to MEU-55 alone. §Goal was updated; the **Out of Scope** table three hundred
lines below it was not. It still read:

```
| Drag reorder on the Transcript and TTS queues | Deferred | MEU-55, MEU-56 | Those MEUs adopt `QueueList`; ... |
```

A prose correction summary could not have surfaced this — only sweeping the old value could, which is
precisely the argument for PR-6. The row is now split (`implementation-plan.md:403-404`):

- **Transcript** — `Deferred | MEU-55`. MEU-55 adopts `QueueList` and inherits reorder.
- **TTS** — `Not planned | none`. MEU-56 (`gui-tts-layout`) inherits the shared `ProgressBar`, not
  `QueueList` (`.agent/context/meu-registry.md:150`), and Phase 11's spec file
  `docs/build-plan/11-page-layout.md` **does not exist yet** — MEU-50 authors it
  (`docs/BUILD_PLAN.md:36`) — so there is no specified TTS reorder behaviour to defer. Confirmed:
  `docs/build-plan/` contains `00`–`10` and no `11-page-layout.md`.

**Re-sourcing came with it.** All four sites citing `.agent/context/meu-registry.md:149-150` for the
QueueList-adoption claim were checked against that file. Line 149 says MEU-55 builds Transcript
channel cards "on the `QueueCard` anatomy … plus per-card ▲ ▼ and ⋮ menu" — it does **not** state
`QueueList` adoption. The claim's real source is
`.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md:134-136` ("MEU-55 then adopts
`QueueList` for Transcript channel cards and **inherits reorder for free**"), with MEU-55's dependency
row at `:84` naming MEU-49. §Goal (`:30-33`), the Out-of-Scope row (`:401`), the F8 correction row
(`:520`) and `DND_OPT_IN_RULE`'s note in `named-sets.json` now cite that instead. Only the TTS half
was ever backed by `meu-registry.md:150`; that citation is retained where it applies.

S4's own four changed values were added to the census table and swept in the same run, and so were
S5's (registering the census script itself as `CORRECTION_CENSUS`), S6's (`INHERITED_NAMES`) and
C3's (the key count those registrations moved, 82 -> 83 -> 84; C2's superseded intermediate values
are swept as C3 variants so nothing is left unaccounted). The census covers the corrections it
caused, including its own.

### S5 and S6 — corrections the census caused

Running the census twice more, once per correction it triggered, surfaced two further gaps. Both are
recorded as self-review entries 4 and 5 in the plan's `## Round 1 Review Corrections` section.

- **S5.** `run-correction-census.ps1` printed and referenced the name `CORRECTION_CENSUS`, which was
  defined nowhere — the plan's own single-statement rule, broken by the tool enforcing it. It is now
  a registered key, and the plan states why task row 12 verifies five plan-local scripts while six
  exist: the census is a plan-review-time tool and no execution row depends on it.
- **S6.** Diffing every `` `NAME` ``-quoted token in both plan files against this project's keys
  showed 80 NAMEs referenced and 8 unresolved. Six are defined in earlier Phase 10 projects
  (`BULK_REORDER_ALGORITHM`, `COMMAND_MODULE_RULE`, `DEAD_REGION_RULE`, `MOUNT_GATE_PHASE_SCOPES`,
  `RETIRED_TOOLBAR_CONTROLS` in `2026-09-02-p10-queue-card-migration/named-sets.json`; `FROZEN_GLOBS`
  in `2026-08-28-p10-queue-card-foundations/named-sets.json`), and two — `ELECTRON_RUN_AS_NODE` and
  `PENDING` — are not named sets at all. The plan header asserted every set was "defined exactly once
  in `named-sets.json`", so a reader chasing `COMMAND_MODULE_RULE` found nothing and no pointer. The
  six are **not** copied forward, because a duplicated definition is one that can drift; the new
  `INHERITED_NAMES` key lists each with the file it resolves against, records the two non-set tokens,
  and the header now states the exception. Re-running the diff leaves exactly those two unresolved.

`named-sets.json` is now **84** keys.

### Full value table (125 sweeps)

Every row's receipt is under `C:/Temp/av-kit/census/`. `Hits` is the untruncated count from that
receipt; `Exit` is `rg`'s own exit code (0 = matched, 1 = no match, both valid).

| # | Corr | Dir | Value swept | Exit | Hits | Receipt |
|---|---|---|---|---|---|---|
| 1 | F1 | new | `REORDER_SINGLE_FLIGHT_RULE` | 0 | 8 | `census-single-flight-rule-new.txt` |
| 2 | F1 | variant | `createSingleFlight` | 0 | 3 | `census-single-flight-rule-variant1.txt` |
| 3 | F1 | variant | `reorder-single-flight.ts` | 0 | 6 | `census-single-flight-rule-variant2.txt` |
| 4 | F1 | variant | `reorder-single-flight.test.ts` | 0 | 2 | `census-single-flight-rule-variant3.txt` |
| 5 | F1 | variant | `tryAcquire` | 0 | 4 | `census-single-flight-rule-variant4.txt` |
| 6 | F1 | variant | `single-flight` | 0 | 11 | `census-single-flight-rule-variant5.txt` |
| 7 | F1 | new | `AC-49.31` | 0 | 4 | `census-single-flight-acs-new.txt` |
| 8 | F1 | variant | `AC-49.32` | 0 | 3 | `census-single-flight-acs-variant1.txt` |
| 9 | F1 | variant | `AC-49.33` | 0 | 1 | `census-single-flight-acs-variant2.txt` |
| 10 | F1 | variant | `AC-49.34` | 0 | 2 | `census-single-flight-acs-variant3.txt` |
| 11 | F1 | variant | `AC-49.35` | 0 | 3 | `census-single-flight-acs-variant4.txt` |
| 12 | F1 | new | `\| 4a \|` | 0 | 2 | `census-single-flight-rows-new.txt` |
| 13 | F1 | variant | `4a` | 0 | 3 | `census-single-flight-rows-variant1.txt` |
| 14 | F2 | old | `after removal` | 0 | 1 | `census-move-to-index-after-removal-old.txt` |
| 15 | F2 | new | `PRE-MOVE` | 0 | 2 | `census-move-to-index-after-removal-new.txt` |
| 16 | F2 | variant | `pre-move` | 0 | 2 | `census-move-to-index-after-removal-variant1.txt` |
| 17 | F2 | variant | `FINAL index` | 0 | 3 | `census-move-to-index-after-removal-variant2.txt` |
| 18 | F2 | variant | `final index` | 1 | 0 | `census-move-to-index-after-removal-variant3.txt` |
| 19 | F2 | variant | `arrayMove` | 0 | 4 | `census-move-to-index-after-removal-variant4.txt` |
| 20 | F3 | new | `DND_TOUCH_ACTION_RULE` | 0 | 5 | `census-touch-action-new.txt` |
| 21 | F3 | variant | `touch-none` | 0 | 3 | `census-touch-action-variant1.txt` |
| 22 | F3 | variant | `touchAction === 'none'` | 0 | 3 | `census-touch-action-variant2.txt` |
| 23 | F3 | variant | `AC-49.36` | 0 | 4 | `census-touch-action-variant3.txt` |
| 24 | F4 | old | `npx --prefix ui playwright test` | 0 | 5 | `census-e2e-run-command-old.txt` |
| 25 | F4 | new | `npm --prefix ui run test:e2e` | 0 | 6 | `census-e2e-run-command-new.txt` |
| 26 | F4 | variant | `E2E_RUN_COMMAND` | 0 | 6 | `census-e2e-run-command-variant1.txt` |
| 27 | F4 | variant | `playwright test` | 0 | 5 | `census-e2e-run-command-variant2.txt` |
| 28 | F5 | new | `RED_PHASE_ORACLE` | 0 | 7 | `census-red-phase-oracle-new.txt` |
| 29 | F5 | variant | `assert-red-phase.ps1` | 0 | 8 | `census-red-phase-oracle-variant1.txt` |
| 30 | F5 | variant | `RED_PHASE_REQUIRED_ACS` | 0 | 6 | `census-red-phase-oracle-variant2.txt` |
| 31 | F5 | variant | `RED_PHASE_TEST_FILES` | 0 | 3 | `census-red-phase-oracle-variant3.txt` |
| 32 | F5 | variant | `\| 3a \|` | 0 | 2 | `census-red-phase-oracle-variant4.txt` |
| 33 | F5 | variant | `-Census` | 0 | 3 | `census-red-phase-oracle-variant5.txt` |
| 34 | F6 | new | `REORDER_FEEDBACK_TIER` | 0 | 6 | `census-feedback-tier-new.txt` |
| 35 | F6 | variant | `TESTING_LIBRARY_ADOPTION` | 0 | 3 | `census-feedback-tier-variant1.txt` |
| 36 | F6 | variant | `GUI_ENFORCEMENT_FALLBACK` | 0 | 3 | `census-feedback-tier-variant2.txt` |
| 37 | F7 | old | `the order changed` | 0 | 3 | `census-exact-order-old.txt` |
| 38 | F7 | new | `[B,C,A,D]` | 0 | 4 | `census-exact-order-new.txt` |
| 39 | F7 | variant | `[A,B,C,D]` | 0 | 4 | `census-exact-order-variant1.txt` |
| 40 | F7 | variant | `[B,A,C,D]` | 0 | 3 | `census-exact-order-variant2.txt` |
| 41 | F7 | variant | `[A,D,B,C]` | 0 | 1 | `census-exact-order-variant3.txt` |
| 42 | F8 | old | `438` | 0 | 1 | `census-vitest-baseline-old.txt` |
| 43 | F8 | new | `439` | 0 | 4 | `census-vitest-baseline-new.txt` |
| 44 | F8 | variant | `VITEST_BASELINE_COUNT` | 0 | 4 | `census-vitest-baseline-variant1.txt` |
| 45 | F8 | old | `MEU-56` | 0 | 7 | `census-inheritance-meu-old.txt` |
| 46 | F8 | new | `MEU-55` | 0 | 12 | `census-inheritance-meu-new.txt` |
| 47 | F8 | variant | `inherit` | 0 | 12 | `census-inheritance-meu-variant1.txt` |
| 48 | S1 | new | `-RequiredAcIds` | 0 | 3 | `census-required-ac-ids-new.txt` |
| 49 | S1 | variant | `clause (e)` | 0 | 2 | `census-required-ac-ids-variant1.txt` |
| 50 | S1 | variant | `RED_PHASE_REQUIRED_ACS` | 0 | 6 | `census-required-ac-ids-variant2.txt` |
| 51 | S2 | old | `<the VITEST_EXIT from row 3>` | 0 | 1 | `census-vitest-exit-placeholder-old.txt` |
| 52 | S2 | new | `$vitest` | 0 | 4 | `census-vitest-exit-placeholder-new.txt` |
| 53 | S2 | variant | `VITEST_EXIT` | 0 | 1 | `census-vitest-exit-placeholder-variant1.txt` |
| 54 | S3 | old | `pwsh -NoProfile -Command "$` | 1 | 0 | `census-shell-expansion-old.txt` |
| 55 | S3 | new | `SHELL_EXPANSION_RULE` | 0 | 1 | `census-shell-expansion-new.txt` |
| 56 | S3 | variant | `PLAN_GATE_SCRIPT` | 0 | 9 | `census-shell-expansion-variant1.txt` |
| 57 | S3 | variant | `assert-plan-gates.ps1` | 0 | 9 | `census-shell-expansion-variant2.txt` |
| 58 | S3 | new | `-Gate ` | 0 | 6 | `census-plan-gate-names-new.txt` |
| 59 | S3 | variant | `-Gate Deps` | 0 | 1 | `census-plan-gate-names-variant1.txt` |
| 60 | S3 | variant | `-Gate E2eCensus` | 0 | 1 | `census-plan-gate-names-variant2.txt` |
| 61 | S3 | variant | `-Gate BuildPlanAudit` | 0 | 1 | `census-plan-gate-names-variant3.txt` |
| 62 | S3 | variant | `-Gate Unchecked` | 0 | 1 | `census-plan-gate-names-variant4.txt` |
| 63 | S3 | variant | `-Gate ApiSkip` | 0 | 1 | `census-plan-gate-names-variant5.txt` |
| 64 | S3 | variant | `-Gate Reflection` | 0 | 1 | `census-plan-gate-names-variant6.txt` |
| 65 | S3 | old | `-Pattern 'AC-49\.').Count` | 0 | 1 | `census-fic-ac-check-old.txt` |
| 66 | S3 | new | `assert-handoff-acs.ps1 -Only MEU-49` | 0 | 2 | `census-fic-ac-check-new.txt` |
| 67 | S3 | variant | `HANDOFF_AC_CHECK` | 0 | 6 | `census-fic-ac-check-variant1.txt` |
| 68 | S3 | old | `the **four** plan-local` | 1 | 0 | `census-row12-script-count-old.txt` |
| 69 | S3 | new | `the **five** plan-local` | 0 | 1 | `census-row12-script-count-new.txt` |
| 70 | S3 | variant | `four '-SelfTest' receipts` | 1 | 0 | `census-row12-script-count-variant1.txt` |
| 71 | S3 | variant | `five '-SelfTest' receipts` | 0 | 1 | `census-row12-script-count-variant2.txt` |
| 72 | S3 | variant | `Three self-tested` | 1 | 0 | `census-row12-script-count-variant3.txt` |
| 73 | S3 | variant | `Five self-tested` | 0 | 1 | `census-row12-script-count-variant4.txt` |
| 74 | S3 | old | `6 cases, baseline 439` | 1 | 0 | `census-red-selftest-cases-old.txt` |
| 75 | S3 | new | `8 self-test cases` | 0 | 1 | `census-red-selftest-cases-new.txt` |
| 76 | S3 | variant | `8 cases` | 0 | 2 | `census-red-selftest-cases-variant1.txt` |
| 77 | S3 | variant | `6 cases` | 0 | 1 | `census-red-selftest-cases-variant2.txt` |
| 78 | C1 | old | `AC-49.1–49.30` | 1 | 0 | `census-ac-count-old.txt` |
| 79 | C1 | new | `AC-49.1–49.36` | 0 | 3 | `census-ac-count-new.txt` |
| 80 | C1 | variant | `AC-49.30` | 0 | 3 | `census-ac-count-variant1.txt` |
| 81 | C1 | variant | `AC-49.36` | 0 | 4 | `census-ac-count-variant2.txt` |
| 82 | C1 | variant | `**36**` | 0 | 1 | `census-ac-count-variant3.txt` |
| 83 | C1 | variant | `30 ACs` | 1 | 0 | `census-ac-count-variant4.txt` |
| 84 | C2 | old | `72 to **80**` | 1 | 0 | `census-named-set-key-count-old.txt` |
| 85 | C2 | new | `72 to **84**` | 0 | 1 | `census-named-set-key-count-new.txt` |
| 86 | C2 | variant | `80 keys` | 1 | 0 | `census-named-set-key-count-variant1.txt` |
| 87 | C2 | variant | `82 keys` | 1 | 0 | `census-named-set-key-count-variant2.txt` |
| 88 | C2 | variant | `78 keys` | 1 | 0 | `census-named-set-key-count-variant3.txt` |
| 89 | S4 | old | `Drag reorder on the Transcript and TTS queues` | 0 | 1 | `census-oos-tts-row-old.txt` |
| 90 | S4 | new | `Drag reorder on the TTS queue` | 0 | 1 | `census-oos-tts-row-new.txt` |
| 91 | S4 | variant | `Drag reorder on the Transcript queue` | 0 | 1 | `census-oos-tts-row-variant1.txt` |
| 92 | S4 | variant | `MEU-55, MEU-56` | 1 | 0 | `census-oos-tts-row-variant2.txt` |
| 93 | S4 | variant | `Those MEUs adopt` | 0 | 1 | `census-oos-tts-row-variant3.txt` |
| 94 | S4 | old | `meu-registry.md:149-150` | 0 | 1 | `census-queuelist-source-old.txt` |
| 95 | S4 | new | `p11-page-layout-session-grouping.md:134-136` | 0 | 4 | `census-queuelist-source-new.txt` |
| 96 | S4 | variant | `meu-registry.md:149` | 0 | 1 | `census-queuelist-source-variant1.txt` |
| 97 | S4 | variant | `meu-registry.md:150` | 0 | 4 | `census-queuelist-source-variant2.txt` |
| 98 | S4 | variant | `:134-136` | 0 | 4 | `census-queuelist-source-variant3.txt` |
| 99 | S4 | old | `adopts the shared progress primitive` | 1 | 0 | `census-tts-primitive-old.txt` |
| 100 | S4 | new | `inherits the shared 'ProgressBar'` | 0 | 2 | `census-tts-primitive-new.txt` |
| 101 | S4 | variant | `shared progress primitive` | 1 | 0 | `census-tts-primitive-variant1.txt` |
| 102 | S4 | variant | `inherits the shared ProgressBar` | 1 | 0 | `census-tts-primitive-variant2.txt` |
| 103 | S4 | old | `Three further defects` | 1 | 0 | `census-selfreview-count-old.txt` |
| 104 | S4 | new | `Four further defects` | 0 | 1 | `census-selfreview-count-new.txt` |
| 105 | S4 | variant | `three more defects` | 1 | 0 | `census-selfreview-count-variant1.txt` |
| 106 | S4 | variant | `four self-review` | 1 | 0 | `census-selfreview-count-variant2.txt` |
| 107 | S4 | variant | `three self-review` | 1 | 0 | `census-selfreview-count-variant3.txt` |
| 108 | S5 | old | `two plan-local scripts, both already` | 1 | 0 | `census-census-name-old.txt` |
| 109 | S5 | new | `CORRECTION_CENSUS` | 0 | 2 | `census-census-name-new.txt` |
| 110 | S5 | variant | `three plan-local scripts, all already` | 0 | 1 | `census-census-name-variant1.txt` |
| 111 | S5 | variant | `run-correction-census.ps1` | 0 | 3 | `census-census-name-variant2.txt` |
| 112 | S5 | variant | `the **five** plan-local` | 0 | 1 | `census-census-name-variant3.txt` |
| 113 | S5 | variant | `the **six** plan-local` | 1 | 0 | `census-census-name-variant4.txt` |
| 114 | C3 | old | `72 to **83**` | 1 | 0 | `census-key-count-84-old.txt` |
| 115 | C3 | new | `72 to **84**` | 0 | 1 | `census-key-count-84-new.txt` |
| 116 | C3 | variant | `72 to **82**` | 1 | 0 | `census-key-count-84-variant1.txt` |
| 117 | C3 | variant | `82 keys` | 1 | 0 | `census-key-count-84-variant2.txt` |
| 118 | C3 | variant | `83 keys` | 1 | 0 | `census-key-count-84-variant3.txt` |
| 119 | C3 | variant | `84 keys` | 1 | 0 | `census-key-count-84-variant4.txt` |
| 120 | S6 | new | `INHERITED_NAMES` | 0 | 2 | `census-inherited-names-new.txt` |
| 121 | S6 | variant | `COMMAND_MODULE_RULE` | 0 | 6 | `census-inherited-names-variant1.txt` |
| 122 | S6 | variant | `BULK_REORDER_ALGORITHM` | 0 | 4 | `census-inherited-names-variant2.txt` |
| 123 | S6 | variant | `FROZEN_GLOBS` | 0 | 2 | `census-inherited-names-variant3.txt` |
| 124 | S6 | variant | `ELECTRON_RUN_AS_NODE` | 0 | 8 | `census-inherited-names-variant4.txt` |
| 125 | S6 | variant | `Six NAMEs are the exception` | 0 | 1 | `census-inherited-names-variant5.txt` |

### Round 3 resubmission

The same plan artifact is re-dispatched, now six files — the added one is
`run-correction-census.ps1`, the census script itself, which is part of the plan and reviewable like
the other two. The content changes since Round 2 are `implementation-plan.md:403-404` (the split Out-of-Scope row),
the four re-sourced citations, the two new `named-sets.json` keys `CORRECTION_CENSUS` and
`INHERITED_NAMES` (82 -> 84), the plan header's inheritance exception, task row 12's five-not-six
note, and self-review entries 4 and 5 recording all of it. No AC changed, no task row was added or
removed, and no validation command changed.

F1–F8 were explicitly **not adjudicated** in Round 2 (withheld by the PR-6 stop) and are the
substantive question for Round 3. Round 3 of 3.

---
date: 2026-09-03
review_mode: plan
target_plan: docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md
verdict: changes_required
round: 3
findings_count: 7
template_version: "2.1"
requested_verbosity: standard
agent: gpt-5.6-sol (Codex independent reviewer)
---

## Round 3 — Substantive Review (2026-09-03)

### Intent Anchor

MEU-49 must add accessible pointer/touch/keyboard drag reorder without weakening the existing
kebab and Alt+Arrow alternatives, without allowing absolute-permutation PUTs to clobber each
other, and with execution gates that distinguish the intended Red/Green/closeout states. No
MEU-49 implementation has started.

### F1–F8 Adjudication

| Finding | Status | Evidence and adjudication |
|---|---|---|
| F1 | **NOT CLOSED** | The synchronous primitive is testable (`implementation-plan.md:157`), but the integration design is incomplete. The bulk fold is owned inside `useQueueBulk.moveSelected()` and returns `void` (`ui/src/renderer/src/lib/queue/use-queue-bulk.ts:93,141-160`), so a page caller cannot acquire before the fold and release after its hidden async reconcile. The plan neither changes that hook nor names another whole-fold integration point (`implementation-plan.md:290-299`; `task.md:40`). A per-page ref also loses exclusion on route unmount/remount even while the old request continues; the router mounts these as separate route components (`ui/src/renderer/src/router.tsx:28-50`), while AC-49.31 explicitly makes instances independent. AC-49.34 covers rejection only, not unmount/remount (`implementation-plan.md:277`). |
| F2 | **CLOSED** | `MOVE_TO_INDEX_CONTRACT` now fixes both indices against the pre-move array and pins forward, backward, and adjacent examples; AC-49.5 requires exact orders (`named-sets.json:84`; `implementation-plan.md:154`). The E2E forward cases require `[B,C,A,D]` and reject `[B,A,C,D]` (`implementation-plan.md:310,314`). |
| F3 | **CLOSED** | The unit contract requires `touch-none` and rejects the competing touch-action classes (`implementation-plan.md:193`); Electron verifies computed `touchAction === 'none'` (`implementation-plan.md:316`). |
| F4 | **CLOSED** | `E2E_RUN_COMMAND` is the correct package-script form (`named-sets.json:181`; `implementation-plan.md:480-491`). Independently, `npm --prefix ui run test:e2e -- --list` exited 0 and collected 73 tests in 12 files. The full run also collected all 73, rather than the former 0-test false run. |
| F5 | **NOT CLOSED** | The new oracle is fail-closed in isolation, but it cannot certify the plan's actual Red topology. Row 3 writes tests importing two modules that rows 4/4a do not create until after the oracle (`task.md:33-36`), so ordinary Vitest collection failure gives neither `numTotalTests > 439` nor failing assertion names. Further, clause (e) requires all 27 listed AC ids to be failing (`assert-red-phase.ps1:153-165`), although the list includes preservation ACs that should already pass on the unstarted tree: existing direction behavior (AC-49.4, `implementation-plan.md:153`), no opt-in drag DOM (AC-49.11, `:194`), and retained kebab/Alt+Arrow paths (AC-49.23, `:273`). The synthetic self-test never models either condition. |
| F6 | **NOT CLOSED** | The canonical Button and G35 feedback portions are closed (`implementation-plan.md:358-371`), but G37 is still redefined rather than satisfied. Canon says “Use `userEvent.setup()`” (`.agent/docs/emerging-standards.md:1212-1218`); the plan instead requires the hand-rolled helper (`task.md:33`) and weakens the named rule to “Prefer” (`named-sets.json:295`). `TESTING_LIBRARY_ADOPTION` labels the exception “Human-approved” without an on-disk human decision anchor (`named-sets.json:171-179`). A review correction is not human approval. |
| F7 | **CLOSED** | Both pointer E2E ACs now require the exact four-id result and name the unchanged/post-removal wrong orders (`implementation-plan.md:310,314`; `task.md:41`). |
| F8 | **CLOSED** | The live Vitest baseline is 439 (`implementation-plan.md:441-442`), independently reproduced as 439/439 in 54 files. The Goal and split Out-of-Scope rows now distinguish MEU-55/QueueList from MEU-56/ProgressBar with the correct sources (`implementation-plan.md:32-36,403-404`). |

### Current Findings

| ID | Severity | Rubric | Finding | Required correction |
|---|---|---|---|---|
| R3-F1 | High | PR-3, PR-5, PR-8 | **F1 remains open: the per-page single-flight design does not cover the bulk owner's async lifetime or a route remount.** `moveSelected()` hides the whole fold behind a `void` API, so the page cannot implement the promised acquire-before-fold/release-after-reconcile contract without an unplanned `use-queue-bulk.ts` change. A remount creates an independent gate while the old request may still settle. While held, only drag handles are specified as disabled; kebab/Alt+Arrow attempts return silently, so the feedback policy is unequal even though the transiently disabled handle itself is reasonable. | Define an explicit, listed integration boundary for the whole bulk fold and a queue-lifetime lock that survives route remount (or cancel/await the old mutation before remount can issue another). Specify consistent unavailable feedback for every competing entry point. Add deferred-promise tests for bulk-vs-single, both completion orders, unmount/remount, rejection, and all page entry paths. |
| R3-F2 | High | PR-4, PR-8 | **F5 remains open: a correctly written Red suite cannot satisfy the oracle.** Missing new modules fail during collection before the oracle's count/name clauses, and regression-preservation ACs are incorrectly required to fail. The passing 8-case self-test exercises only fabricated flat reports (`assert-red-phase.ps1:170-185,230-305`), not the row-3-before-row-4 sequence. | Redesign the Red evidence around the actual task order. Require failure only for behavior expected to be absent, handle targeted new-module collection failures explicitly if that is the chosen TDD boundary, and do not require already-true preservation ACs to fail. Add self-tests for the real Vitest collection shape and for mixed red/green ACs. |
| R3-F3 | Medium | PR-5, PR-6 | **F6's G37 branch is still an unsupported waiver.** The local standard mandates actual Testing Library `userEvent.setup()`; a similarly named custom object is not that API, and the claimed human-approved exception has no human-decision evidence. The follow-up is only an instruction to raise a future MEU, not an existing tracked item. | Use `@testing-library/user-event` for the new interaction tests, or obtain and cite an actual human-approved exception with a concrete tracked follow-up. Do not weaken the canonical rule in `G37_RULE`. |
| R3-F4 | High | PR-4, PR-8 | **`PLAN_GATE_SCRIPT` is not executable in the declared task lifecycle.** H1-1 runs `Unchecked` before H1-2–H2-5, but `Test-Unchecked` scans every `[ ]`, including its own row and all future rows (`task.md:46`; `assert-plan-gates.ps1:184-202`). It therefore cannot pass without prematurely marking unevidenced future work complete. `ApiSkip` also failed live because `git status ... 2>&1` merged a denied global-ignore warning into the porcelain array and reported two fictitious API modifications (`assert-plan-gates.ps1:448-456`). The toy `New-GoodTree` contains only one already-complete task row and calls `Test-ApiUntouched` without invoking Git (`assert-plan-gates.ps1:275-329`), so its 24 passing cases do not cover either real path. | Scope `Unchecked` to rows that must precede H1-1 (and reject `[/]` as well as `[ ]`), or move it to a point where all rows may legitimately be terminal. Self-test against the real phase shape. Make `ApiSkip` capture porcelain stdout separately from diagnostics and self-test the actual Git invocation/warning case. |
| R3-F5 | High | PR-4, PR-8 | **The E2E gates can pass with none of AC-49.25–49.29/49.36 implemented.** Today's unstarted tree already meets both floors: 67 static declarations and 73 runtime cases. After merely registering `queue-card-drag-handle`, `E2eCensus` passes because it checks only the unchanged floor, absence of `dragTo(`, and the id substring (`assert-plan-gates.ps1:122-158`). Row 10 repeats `>= 73`/`>= 67` (`task.md:41-42`). The Red census explicitly excludes E2E files, so no deterministic gate proves that the six new E2E cases exist. | Register required E2E AC ids/titles/files as a named set and assert each exists, or require source-backed post-MEU count deltas that cannot be met by the baseline. Keep the runtime run as behavioral proof, but do not use unchanged floors as proof that new cases landed. |
| R3-F6 | Medium | PR-4, PR-7, PR-8 | **Several other validation rows test adjacent text, not their deliverable.** `Deps` performs substring searches and never checks dependency sections or the exact `DND_PACKAGES` ranges (`assert-plan-gates.ps1:92-120`), while row 2 promises exact direct dependencies. `BuildPlanAudit` does not inspect `meu-status.yaml`, the Phase 10 complete state, or the required “Next = Phase 11 / MEU-50” update (`assert-plan-gates.ps1:160-182`; `task.md:43`). H2-3 merely tails the metrics file and H2-5 merely reads the draft, so a missing metrics slug or empty draft exits 0 (`task.md:58,60`). Row 3a also starts its second process as raw `pwsh`, not an RTK-prefixed segment (`task.md:34`). | Parse both manifests and compare exact direct name/range pairs; validate the YAML/rendered status and all three BUILD_PLAN outcomes; assert `METRICS_SLUG` and nonempty draft content; and RTK-prefix every process segment. Add negative fixtures for each claimed condition, not only nearby text. |
| R3-F7 | Medium | PR-6, PR-9 | **The correction census is mechanically complete but semantically incomplete for S6.** S6 changed the universal “all names are local” header claim, yet its census entry declares `old = ''` and sweeps only the new exception/name variants (`run-correction-census.ps1:128-132`). The equivalent old claim remains live in `task.md:14` (“every capitalised NAME below is defined there once”), even though `COMMAND_MODULE_RULE` and other task names are inherited. That line is absent from the 21-survivor disposition table because no old/semantic sweep could find it. | Add the old universal-claim wording and semantic variants to S6, update or explicitly disposition `task.md:14`, rerun the census, and reconcile the new receipt/table counts. |

### Independent Verification Performed

| Check | Result |
|---|---|
| `CORRECTION_CENSUS -SelfTest` | Exit 0: 5 cases passed. |
| Independent census live run | Exit 0: 45 values, 80 variants, 325 matching lines; zero new-value misses. |
| Census receipt integrity | 125 table rows, 125 per-sweep receipts, zero line-count mismatches; both indexes are 580 lines; no `head`, `Select-Object -First`, or tee in the census implementation. |
| OLD survivor inspection | All 21 recorded OLD hits are honest correction-history or negative-test quotations, including S4. R3-F7 is an omitted semantic sweep, not a dishonest recorded disposition. |
| `assert-red-phase.ps1 -SelfTest` | Exit 0: 8 synthetic cases, baseline 439, 27 required AC ids. Substantive lifecycle defect remains per R3-F2. |
| `assert-plan-gates.ps1 -SelfTest` | Exit 0: 24 synthetic cases across 6 gates. |
| Six live plan gates | `Deps=1`, `E2eCensus=1`, `BuildPlanAudit=1`, `Unchecked=1`, `ApiSkip=1`, `Reflection=1`. The claimed five-fail/ApiSkip-pass result was not reproduced; ApiSkip falsely classified a Git warning as two modifications. |
| Vitest baseline and JSON shape | Exit 0: 439 passed in 54 files; 54 top-level `testResults`, each with flat `assertionResults`. Empty failing results fail closed, but the actual row ordering/green preservation cases are not self-tested. |
| E2E listing/static census | Exit 0: 73 runtime tests in 12 files; 67 static `test(` declarations across 10 `*.test.ts` files. |
| Full E2E after fresh build | Build exit 0. Playwright collected all 73, then exited 1 with 72 `electronApplication.firstWindow` closures and 1 sidecar test passed. This confirms F4's command/count correction, but is not a green baseline receipt in this reviewer sandbox. |
| Button claim | Confirmed ref forwarding at `Button.tsx:37-50`, default `type="button"`, and `...rest` spread at `:62-68`. |
| Missing-document claims | `docs/gui-element-reference.md` absent; `docs/build-plan/11-page-layout.md` absent; BUILD_PLAN line 36 assigns the latter to MEU-50. |
| AC/name consistency | 36 unique plan AC rows; every task AC reference resolves. 84 local named-set keys and all 6 inherited keys resolve; the only non-set unresolved tokens are `ELECTRON_RUN_AS_NODE` and `PENDING`. |
| Task dependency order | Topologically valid after 3a/4a insertion. The problem is H1-1's gate predicate, not its dependency edge. |
| Plan-local script count | Six `.ps1` files exist. Excluding the already-used review-time census from row 12's five execution checks is reasonable by itself. |
| Shell-expansion sweep | Three `pwsh -NoProfile -Command` text hits remain; the two executable commands are variable-free. R3-F6 records their separate non-discrimination issue. |

### Checklist Results

| Rule | Result | Notes |
|---|---|---|
| PR-1 Scope integrity | Partial | Core MEU scope is bounded; the bulk-gate integration needs an explicitly listed hook/module boundary. |
| PR-2 Current-state grounding | Pass | Current pages, command modules, shared bulk hook, router, schemas, and baselines were read directly. |
| PR-3 Contract completeness | Fail | F1 does not define queue-lifetime/remount behavior or an implementable whole-fold boundary. |
| PR-4 Executability | Fail | Red, H1-1, ApiSkip, E2E-presence, and several closeout validators do not discriminate their claimed states. |
| PR-5 Correctness/accessibility | Fail | F1 concurrency/feedback and F6/G37 remain unresolved. Touch action and drag/file-drop isolation contracts are otherwise adequate. |
| PR-6 Correction readiness | Fail | Receipts/dispositions are intact, but S6 omitted the old semantic claim and left `task.md:14` contradictory. |
| PR-7 Supersession | Partial | F8/S4 sources are corrected; dependency and phase-exit gates do not prove their full supersession outcomes. |
| PR-8 Anti-false-pass | Fail | R3-F2 and R3-F4–F6 include both false-pass and false-fail execution gates. |
| PR-9 Machine-readable carry-forward | Partial | Key counts and inherited resolution are sound; the task header/census inventory still contradict them. |

### Verdict

**changes_required**

F2, F3, F4, F7, and F8 are closed. F1, F5, and the G37 branch of F6 are not. The task also contains
an impossible H1-1 gate, a live-failing ApiSkip invocation, unchanged-baseline E2E gates that do
not prove the new cases exist, and other validators that can accept the wrong artifact state.
These are substantive correctness, executability, and anti-false-pass defects, not clerical issues.

This is Round 3 of 3. The `changes_required` verdict reaches `PLAN_REVIEW_ROUND_CAP`; execution must
HARD STOP until the human provides direction.

### Follow-up Actions

1. Human adjudication is required because the plan-review round cap is reached.
2. If a correction round is authorized, resolve R3-F1–R3-F7 and rerun the full census, including
   the omitted S6 universal-claim sweep.
3. Do not begin implementation from this plan in its current state.

---

## Corrections Applied — Round 4 (implementor, 2026-09-03)

**Authorization:** the human's chat message *"Authorize a round-4 correction pass"* (`USER_EXPLICIT`).
Round 3 reached `PLAN_REVIEW_ROUND_CAP` and HARD STOPped; this pass exists only because the human
lifted that stop. No implementation has started — the `ui/` tree is still unmodified.

### R3-F1 … R3-F7 resolution

| Finding | Resolution | Evidence |
|---|---|---|
| **R3-F1** Single-flight integration incomplete: `moveSelected()` returns `void`, so no caller can wrap the whole fold; a per-page ref loses exclusion across route unmount/remount | Ownership moved **into** `use-queue-bulk.ts` (the only code that sees the whole fold), and the gate's lifetime moved from a component ref to a **module-level map keyed by `REORDER_QUEUE_KEYS`**, so unmount/remount while a PUT is in flight still excludes. `use-queue-bulk.ts` gains a required `queueKey` option. AC-49.33 now asserts **both** completion orders; new **AC-49.37** covers the module-map lifetime, unmount/remount mid-flight, and cross-queue independence | `implementation-plan.md:292` (AC-49.33), `:295` (AC-49.37), §4/§5 file lists, `task.md` row 8 |
| **R3-F2** The Red oracle is unsatisfiable: row 3 writes tests importing modules rows 4/4a have not created, and preservation ACs are required to fail | **Measured rather than argued.** A live Vitest JSON probe shows a missing *module* aborts collection for its whole file (`status: failed`, empty `assertionResults`, non-empty top-level `message`, contributes **0** to `numTotalTests`), while a missing *named export* from an existing module does **not** — that file collects and the assertion fails normally. The reviewer and I both held the second case to behave like the first; it does not. The probe ships in the plan folder as `vitest-shape-probe.json` and the oracle’s self-test replays it. AC-49.16/49.17 moved out of `queue-primitives.test.ts` into a **new** `ui/tests/unit/queue-dnd.test.ts`, so every uncollected file is new and subtracts 0 from the 439 baseline, keeping `numTotalTests > 439` satisfiable. New clauses **(b2)**/**(b3)** require each `RED_PHASE_UNCOLLECTED_FILES` entry to name its own specifier and forbid any *other* non-empty message. On the second half: AC-49.11, AC-49.14 and AC-49.23 are now labelled **preservation** and registered in `RED_PHASE_PRESERVATION_ACS` — the oracle requires them to be *named* in a test but never to *fail*, because demanding that would demand a regression | `named-sets.json` (`VITEST_COLLECTION_FAILURE_SHAPE`, `RED_PHASE_UNCOLLECTED_FILES`, `RED_PHASE_PRESERVATION_ACS`), `implementation-plan.md` §Verification Plan 1a, `:287`, `assert-red-phase.ps1` cases 9–10 |
| **R3-F3** G37’s waiver was labelled `Human-approved` with no approval on disk | `G37_RULE` is restored **verbatim** — the canonical rule is not weakened. What changed is the label on the scope boundary: it is now `Local Canon`, evidenced by `ui/package.json` declaring no `@testing-library/*` package in any section, so `userEvent.setup()` has no referent in this package and all 54 existing unit files use `ui/tests/unit/helpers/user-event.ts`. MEU-49 adds no new `fireEvent` call site, so it introduces no new divergence. I did not manufacture the human approval that does not exist; package-wide adoption is instead registered as **OQ-5** against session 23 (`p11-layout-canon`) — see *Open question carried to the human* below | `named-sets.json` `G37_RULE`, Out of Scope row, OQ-5 |
| **R3-F4** `PLAN_GATE_SCRIPT` is not executable in the declared task lifecycle: `Unchecked` scans its own row and every future row; `ApiSkip` merged git diagnostics into porcelain and reported two fictitious modifications; the toy fixture covered neither real path | `Test-Unchecked` is scoped to rows **above** the `H1-1` row (the boundary is a parameter, and its disappearance is itself a finding), rejects `[/]` as well as `[ ]`, requires a `[B]` to carry a receipt path or a named follow-up, and fails vacuously-empty scans. `Test-ApiUntouched` now takes stdout and stderr as **separate** parameters and validates each surviving line against the porcelain v1 `XY <path>` shape before believing it; diagnostics go to `Write-Verbose`. The fixture grew with the gates: 53 self-test cases across 8 gates, including negative fixtures for the warning-on-stderr case and for a task table whose H1-1 boundary is missing | `assert-plan-gates.ps1:383-434` (`Unchecked`), `:439-486` (`ApiUntouched`), self-test receipt `C:/Temp/av-kit/r4/plan-gates-selftest2.txt` |
| **R3-F5** The E2E gates can pass with none of AC-49.25–49.29/49.36 implemented: the unstarted tree already meets both floors | Two changes. The floors are now the **post**-MEU pair `E2E_POST_MEU_STATIC_FLOOR` (73) / `E2E_POST_MEU_RUNTIME_FLOOR` (79); the pre-MEU 67/73 pair is labelled as such and is never a pass condition. More importantly a count floor is no longer the proof at all: the new `E2E_REQUIRED_CASES` map pairs each integration AC id with the spec file that **owns** it, and `Test-E2eCensus` requires a `test(` title carrying that id in that file, so the gate can no longer be satisfied by registering a test-id and leaving the cases unwritten. Live on the unstarted tree: 8 problems | `named-sets.json` `E2E_REQUIRED_CASES`, `assert-plan-gates.ps1:254-305`, `task.md` rows 9–10 |
| **R3-F6** Several validation rows test adjacent text, not their deliverable (`Deps` substring search; `BuildPlanAudit` never reads `meu-status.yaml`; H2-3 tails the metrics file; H2-5 reads the commit draft; row 3a starts its second process as raw `pwsh`) | `Test-Deps` parses **both** manifests: each `DND_PACKAGES` entry must appear in `dependencies` (devDependencies is a named failure, not a pass) at the **exact** registered range, must resolve in `package-lock.json` to a concrete version inside that major, and the rejected packages are swept across all four sections. `Test-BuildPlanAudit` reads the **source** `meu-status.yaml` first — the rendered files can be right while the YAML still says `pending` — then the Phase 10 row and the Next pointer. Two gates are new: `-Gate Metrics` locates the `METRICS_SLUG` row and names every missing `METRICS_ROW_MARKERS` entry, and `-Gate CommitDraft -ReceiptPath …` requires the draft to exist, be non-empty, carry every `COMMIT_DRAFT_MARKERS` marker, carry **no** AI attribution trailer, and keep its subject ≤ 72 chars (it neither commits nor authorises a commit). The RTK prefix was added to the second process in `task.md` row 3a **and** to the same command at `implementation-plan.md:490` — the census caught that second site, which this pass had missed | `assert-plan-gates.ps1:176-249` (`Deps`), `:307-381` (`BuildPlanAudit`), `:514-591` (`Metrics`, `CommitDraft`), `task.md` row 3a / H2-3 / H2-5, `implementation-plan.md:490` |
| **R3-F7** `task.md:14` claimed *every* capitalised NAME is defined once — false on its face; the census omitted the S6 universal-claim sweep | The claim is qualified **and** enforced. `CORRECTION_CENSUS` gains a fail-closed `-Gate S6`: (a) any paragraph making a universal claim about NAMEs without a qualifier token is a finding; (b) every capitalised underscore-joined token in either plan file must resolve to a `named-sets.json` key, `INHERITED_NAMES.value`, or `INHERITED_NAMES.non_set_token_list`. Running it immediately found three tokens the round-2 hand diff had missed (`BUILD_PLAN`, `FAIL_TO_PASS`, `VITEST_EXIT`) and two further unqualified claims in the plan header — i.e. R3-F7 was under-reported, not over-reported | `run-correction-census.ps1`, `named-sets.json` `INHERITED_NAMES`, `implementation-plan.md:12-22`, `task.md:14` |

### What the round-4 census itself caught

The census is the reason three of these landed at all; none were visible from the correction diff:

1. `implementation-plan.md:490` still ran `assert-red-phase.ps1` **without** `rtk proxy` after `task.md`
   row 3a had been fixed — an R3-F6 correction applied at one of its two sites.
2. Two unqualified universal claims survived in `implementation-plan.md` (the header block and the
   round-2 self-review narrative) after only `task.md:14` had been fixed.
3. Three capitalised tokens resolved to nothing. The round-2 self-review had done that diff by hand
   and recorded "80 NAMEs referenced, 8 unresolved, 6 inherited and 2 not named sets"; it was stale
   within a day. All five non-set tokens are now in `INHERITED_NAMES.non_set_token_list`, and the
   diff is a script that re-derives itself on every run rather than a number in prose.

### Census receipts

`run-correction-census.ps1 -ReceiptDir C:/Temp/av-kit/r4/census` — **64 values, 128 variants, 583
hits, S6 0 findings, exit 0**. Consolidated index: `C:/Temp/av-kit/r4/census/census-index.txt`; one
untruncated receipt per sweep beside it; S6 at `census-s6-universal-claims.txt`.

**Zero-hit NEW values: none** — every round-1…round-4 replacement is present where it was claimed.

**Surviving OLD values — per-line disposition (10 values, 22 hits).** Every one is either a
historical record of the defect in the correction tables (which must keep quoting the old value to
be readable) or a live **prohibition** naming the forbidden form:

| Value | Hits | Disposition |
|---|---|---|
| `after removal` | `implementation-plan.md:580` | Historical — the F2 row describing the round-1 defect. |
| `npx --prefix ui playwright test` | `task.md:41`, `:42`, `:96`, `implementation-plan.md:337`, `:582` | Prohibition — each site names the forbidden invocation and says it reports 0 tests and exits 1. Removing the string would remove the warning. |
| `the order changed` | `task.md:41`, `implementation-plan.md:332`, `:580` | Prohibition — each is the negative form ("never a weaker 'the order changed' check"). |
| `438` | `implementation-plan.md:586` | Historical — the F8 row recording the wrong baseline. |
| `MEU-56` | `implementation-plan.md:41`, `:433`, `:586`, `:637`, `:639`, `:640`, `:641` | Correct usage at `:41`/`:433` (MEU-56 inherits the shared `ProgressBar`, **not** `QueueList`); historical at the rest. |
| `<the VITEST_EXIT from row 3>` | `implementation-plan.md:610` | Historical — self-review entry 2 quoting the retired placeholder. |
| `-Pattern 'AC-49\.').Count` | `implementation-plan.md:628` | Historical — self-review entry 3 quoting the retired receipt. |
| `Drag reorder on the Transcript and TTS queues` | `implementation-plan.md:638` | Historical — self-review entry 4 quoting the row the round-2 census caught. |
| `meu-registry.md:149-150` | `implementation-plan.md:646` | Historical — self-review entry 4 recording the re-sourcing. |
| `AC-49.1–49.36` | `implementation-plan.md:588` | Historical — the counts paragraph states the round-1 range before giving the round-4 range. |

### Plan-local scripts — all self-testing green

| Script | Self-test | Receipt |
|---|---|---|
| `assert-red-phase.ps1` (`RED_PHASE_ORACLE`) | PASS — 14 cases, baseline 439, 24 required-red AC ids, 3 preservation, 3 expected-uncollected | `C:/Temp/av-kit/r4/red-selftest2.txt` |
| `assert-plan-gates.ps1` (`PLAN_GATE_SCRIPT`) | PASS — 53 cases across 8 gates | `C:/Temp/av-kit/r4/plan-gates-selftest2.txt` |
| `run-correction-census.ps1` (`CORRECTION_CENSUS`) | PASS — 11 cases (5 sweep, 3 universal-claim, 2 inventory, 1 real-file satisfiability) | `C:/Temp/av-kit/r4/census-selftest.txt` |

Case 10 of the census self-test and case 10 of the Red oracle's are satisfiability proofs, not
harness checks: each feeds the **real** artifacts and requires a **pass**, so "this gate can never
be satisfied" is a claim the scripts refute on every run.

### Open question carried to the human (OQ-5)

R3-F3 asked for either `@testing-library/user-event` adoption or "an actual human-approved exception
with a concrete tracked follow-up". I can produce the follow-up; I cannot produce a human approval
that does not exist on disk, and inventing one is the failure mode `Human-approved` exists to
prevent. So the plan no longer claims an exception at all: it records the package as it is
(`ui/package.json` declares no `@testing-library/*` dependency in any section; all 54 existing unit
files use `ui/tests/unit/helpers/user-event.ts`), labels that `Local Canon`, restores `G37_RULE`
verbatim, and registers package-wide adoption as OQ-5 against session 23. MEU-49 adds no `fireEvent`
call site, so it introduces no new divergence. **The human may overrule this and pull adoption into
MEU-49**, which would touch all 54 unit test files.

### Round 4 resubmission scope

Changed since Round 3: `named-sets.json` (84 → 94 keys, plus the `INHERITED_NAMES` /
`CORRECTION_CENSUS` field corrections at unchanged key count), `assert-red-phase.ps1` (rewritten,
8 → 14 cases), `assert-plan-gates.ps1` (rewritten, 6 → 8 gates, 24 → 53 cases),
`run-correction-census.ps1` (R4 entries + fail-closed `-Gate S6`, 5 → 11 cases), the new
`vitest-shape-probe.json`, `implementation-plan.md` (662 → 783 lines; 36 → 38 ACs) and `task.md`
(rows 3, 3a, 8, 9, 10, 12, H2-3, H2-5 and the header). One new test file appears in the plan
(`ui/tests/unit/queue-dnd.test.ts`); no task row was removed. Round 4 of 3 — proceeding under
explicit human authorization.

---
date: 2026-09-04
review_mode: plan
target_plan: docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md
verdict: changes_required
round: 4
findings_count: 5
template_version: "2.1"
requested_verbosity: standard
agent: gpt-5.6-sol (Codex independent reviewer)
---

## Round 4 — Authorized Recheck (2026-09-04)

### Intent Anchor

MEU-49 must add accessible pointer/touch/keyboard row drag to the two shared `QueueList` consumers
without weakening the existing kebab and Alt+Arrow alternatives, without allowing competing
absolute-permutation PUTs to overwrite one another, and with Red/Green/closeout gates that prove
the work rather than merely print adjacent state. The working tree contains the prior MEU-45–47
queue migration, but no MEU-49 dnd-kit module, handler, test-id, or test has been added; this remains
a plan review.

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|
| R4-F1 | High | **The Vitest collection-shape claim is correct, but the planned Red topology still cannot satisfy clause (e).** Row 3 assigns AC-49.3–49.7, AC-49.31, and AC-49.16/49.17 to the three new files whose modules intentionally do not exist. Those files therefore contribute no `assertionResults`; all eight IDs remain in `RED_PHASE_REQUIRED_ACS`, so clause (e) necessarily reports them as having no failing test. Replaying the exact planned ownership produced `FAIL: RED_PHASE_ORACLE` with those eight IDs. Self-test case 10 hides the contradiction by redistributing every required ID across whichever files collect instead of preserving row 3's ownership. | `task.md:33`; `named-sets.json:206-234,487-499`; `assert-red-phase.ps1:272-283,374-400,605-617` | Add a canonical file→owned-AC map. For expected-uncollected files, prove the file, AC titles, and exact missing specifier through the census/b2 contract, and require ordinary failing assertions only for IDs in files that collect. Make case 10 preserve that real mapping. Alternatively change the task order so all Red files collect before the oracle, then remove the expected-uncollected exception. | Open |
| R4-F2 | High | **The Red census can pass with both new single-flight integration regressions absent.** Row 3 assigns AC-49.37 and AC-49.38 to the page behavior suites, but neither ID is in `RED_PHASE_REQUIRED_ACS` nor `RED_PHASE_PRESERVATION_ACS`. The census/oracle therefore has no obligation to find either title. An exact set comparison reported 38 plan ACs, 31 unit ACs, 29 unit ACs named by row 3, and `AC-49.37, AC-49.38` missing from both Red sets. | `task.md:33`; `implementation-plan.md:295-296`; `named-sets.json:206-234,478-485` | Register AC-49.37 and AC-49.38 as required-red IDs and add a self-test that compares the complete row-3 unit ownership set with required + preservation, so later AC additions cannot silently fall outside the oracle. | Open |
| R4-F3 | High | **The queue-lifetime gate is non-observable to the remounted UI, and AC-49.38 requires an unplanned, contradictory menu change.** The registry contract exports acquisition/release, but no queue-level held getter/subscription. The current page's `busy` state can reflect its own request; a remounted page starts with `busy=false` while the module gate remains held, so it cannot render handles/menu items disabled and will instead present controls whose acquisition silently returns `null`. Separately, `QueueCardMenu` deliberately omits structurally unavailable actions and its item model/rendered button has no disabled state. AC-49.38 says all four reorder items render disabled, yet neither the §5 file list nor task row 8 includes `QueueCardMenu.tsx`. | `named-sets.json:136-144`; `implementation-plan.md:295-320`; `task.md:40`; `ui/src/renderer/src/components/queue/QueueCardMenu.tsx:6-7,165-218,410-423` | Define a reactive queue-held read/subscription surface that survives remount (for example an external-store contract), and test held-state publication/release on success, rejection, unmount, and remount. Add `QueueCardMenu.tsx` and its tests to the plan. Preserve its structural absence rule and disable only reorder items that would otherwise be present, or explicitly source and test a change to that rule; do not require impossible “all four” rendering at list boundaries. | Open |
| R4-F4 | Medium | **`BuildPlanAudit` can pass while the actual `Next:` pointer still names MEU-49.** The gate reads the whole BUILD_PLAN and separately asks whether `Phase 11` and `MEU-50` occur anywhere. Both already occur elsewhere in the current file, including the stale line itself, so after the other five live failures are fixed the unchanged `Next: p10-queue-card-dnd (MEU-49), then Phase 11...` line satisfies the predicate. The self-test removes the forward strings entirely and does not exercise this false-pass shape. | `assert-plan-gates.ps1:359-375,839-847`; `named-sets.json:531-550`; `docs/BUILD_PLAN.md:72`; `task.md:43` | Parse the single `Next:` line and require that field to start from the Phase 11/MEU-50 target while rejecting MEU-49/p10-queue-card-dnd. Add a negative fixture where Phase 11 and MEU-50 remain elsewhere but `Next:` is stale. | Open |
| R4-F5 | Medium | **OQ-5 is still a waiver, and its factual blast-radius premise is false.** `Local Canon` honestly describes the absence of `@testing-library/*` from the manifest and the existence of a local helper; it does not turn that helper into the canonical `userEvent.setup()` API or authorize ignoring verbatim G37. Only 5 of the 54 unit files import the helper, not all 54, and existing unit files also contain direct `.click()` sites. The deferred row names an OQ/session slug, not a concrete MEU whose registered scope contains the adoption. | `named-sets.json:178-181,303-306`; `implementation-plan.md:396-411,436,738-750`; `task.md:33`; `.agent/docs/emerging-standards.md:1212-1218`; `ui/tests/unit/helpers/user-event.ts:1-13,122` | Correct the census. Literal compliance for MEU-49's new interaction tests can be added here without rewriting all 54 files; a package-wide legacy migration can be its own registered MEU. If the human instead wants the local helper used for MEU-49, record that bounded exception as `Human-approved` and bind the package migration to a real MEU ID. | Open |

### R3-F1–R3-F7 Adjudication

| Prior finding | Round 4 status | Evidence and reasoning |
|---|---|---|
| R3-F1 | **NOT CLOSED** | Moving bulk ownership into `use-queue-bulk.ts`, using a keyed module map, holding through reconcile, and releasing in `finally` correctly cover the mutation lifetime (`implementation-plan.md:292,295`; `named-sets.json:136-139`). The visible-feedback half is not implementable after remount and omits/conflicts with `QueueCardMenu.tsx` (R4-F3). |
| R3-F2 | **NOT CLOSED** | Real Vitest confirms the claimed missing-module versus missing-export shapes, and b2/b3 reject an unrelated collection failure. But clause (e) fails under row 3's actual ownership, while case 10 substitutes an artificial ownership distribution (R4-F1). The Red sets also omit AC-49.37/.38 (R4-F2). |
| R3-F3 | **NOT CLOSED** | `G37_RULE` is restored verbatim, but the `Local Canon` rationale contains a false 54-file claim and still functions as an unapproved exception. OQ-5 is not a registered MEU. See R4-F5. |
| R3-F4 | **CLOSED** | `Unchecked` is bounded above H1-1, rejects `[ ]`/`[/]`, validates `[B]`, and fails closed on a missing/vacuous boundary (`assert-plan-gates.ps1:383-434,867-908`). `ApiSkip` separates stderr and validates stdout porcelain (`:439-486,1037-1058`). It passed after a real `509 passed` backend receipt existed. |
| R3-F5 | **CLOSED** | `E2E_REQUIRED_CASES` binds six AC IDs to their owning specs and the static floor is 73, above the current 67 (`named-sets.json:509-529`; `assert-plan-gates.ps1:254-303`). The untouched tree fails with eight specific problems. |
| R3-F6 | **NOT CLOSED** | Exact dependency/lock checks, source-YAML status checks, Metrics, CommitDraft, and both RTK prefixes are real improvements. The phase-exit `Next:` predicate still has the concrete false-pass in R4-F4. |
| R3-F7 | **CLOSED** | The independent full rerun produced 64 values, 128 variants, 583 hits, S6 0, exit 0. The universal-claim and name-inventory checks are fail-closed, all changed values have sweeps, and all ten old-value survivors are honestly historical quotations or live prohibitions. |

### Empirical Vitest Collection Check

The shipped probe's central distinction reproduced against the installed `ui/` Vitest:

- control file: collected and passed;
- missing named export from an existing module: collected, empty suite-level `message`, one failed
  assertion;
- missing module: suite `status=failed`, non-empty `Cannot find module` message, zero
  `assertionResults`, and zero contribution to `numTotalTests`.

The independent probe reported `numTotalTests=2`, `numFailedTests=1`, and three suites
(`C:/Temp/av-kit/r4-vitest-probe/summary.txt`). Therefore the baseline clause `> 439` is satisfiable:
the four existing files can add collected tests while the three new files add zero. Clauses (b2)
and (b3) also close the unrelated-collection-failure hole: each expected file must identify its own
specifier, and every other non-empty suite message is rejected (`assert-red-phase.ps1:186-239`).

That does not rescue clause (e). A synthetic JSON report preserving the task's actual file ownership
had 458 collected tests and the three exact expected collection failures, yet the oracle exited 1:

```text
(e) no failing test covers: AC-49.3, AC-49.4, AC-49.5, AC-49.6, AC-49.7,
AC-49.16, AC-49.17, AC-49.31
FAIL: RED_PHASE_ORACLE
```

Receipt: `C:/Temp/av-kit/r4-vitest-probe/planned-topology-oracle.txt`.

### Gate Execution and Satisfiability

| Check | Exit/result on current unstarted MEU-49 tree | Right reason and eventual passability |
|---|---|---|
| `assert-red-phase.ps1 -SelfTest` | 0 — 14 cases | Harness cases pass, but case 10 is not the real ownership topology (R4-F1). |
| `assert-plan-gates.ps1 -SelfTest` | 0 — 53 cases / 8 gates | Seven gates have credible positive/negative fixtures; BuildPlanAudit omits the stale-Next-with-forward-text case. |
| `run-correction-census.ps1 -SelfTest` | 0 — 11 cases | Case 10 genuinely runs both S6 predicates against the real plan/task and requires zero findings. |
| `run-correction-census.ps1 -Gate S6` | 0 — 0 findings | Correct live result. |
| `assert-handoff-markers.ps1 -SelfTest` | 0 | Positive and negative marker shapes pass. |
| `assert-handoff-acs.ps1 -SelfTest` | 0 | Positive and negative AC coverage shapes pass. |
| `assert-exec-review-dispatch.ps1 -SelfTest` | 0 — 7 cases | Dispatch-verdict shape is satisfiable. |
| `-Gate Deps` | 1 — 6 problems | Correct: three required dnd-kit packages are missing from each manifest surface. Its good fixture proves a completed state can pass. |
| `-Gate E2eCensus` | 1 — 8 problems | Correct: static 67 < 73, six mapped AC cases missing, test-id missing. Its good fixture can pass. |
| `-Gate BuildPlanAudit` | 1 — 5 problems | Correct present failures, but incomplete in the other direction: stale `Next:` can survive and later pass (R4-F4). |
| `-Gate Unchecked` | 1 — 14 open implementation rows | Correct. Rows below H1-1 are intentionally outside this invocation; the good fixture passes. |
| `-Gate ApiSkip` | 1 without prerequisite, then 0 | Correct both ways. It first rejected the missing receipt, then passed with `C:/Temp/av-kit/meu49-pytest.txt` containing `509 passed, 2 warnings`. API porcelain stdout was empty; diagnostics were separate. |
| `-Gate Reflection` | 1 | Correct: the MEU-49 reflection is absent. Complete-marker and negative fixtures show passability. |
| `-Gate Metrics` | 1 | Correct: the MEU-49 metrics row is absent. Full-marker fixture passes. |
| `-Gate CommitDraft` | 1 | Correct: the draft is absent. The good draft fixture passes; empty, missing marker, trailer, and long subject fail. |

Independent baselines also reproduced `54 files, 439 tests passed` for Vitest and `73 tests in 12
files` for Playwright `--list` (`C:/Temp/av-kit/r4-review-unit-baseline.txt`,
`C:/Temp/av-kit/r4-review-e2e-list.txt`). The Electron runtime was not launched.

### Single-Flight and Interaction Design Review

The production entry-point enumeration is otherwise complete for this MEU. Downloader and Convert
each have the single-row page reorder wrapper and the `useQueueBulk.moveSelected` fold; kebab and
Alt+Arrow converge on those page callbacks, and drag will add `onMoveToIndex`. Transcript has a
separate queue and does not opt into the shared `QueueList`; TTS is also outside
`REORDER_QUEUE_KEYS`.

Acquiring before reading `items`, holding across every fold PUT plus refetch/clear, and releasing in
`finally` avoids an error-path deadlock. Unmount does not destroy the async closure, so a settling
request can still release. A never-settling external request remains held, but that is the same
pending-operation condition as the existing page busy state, not a new finite error path. The map
has a fixed two-key domain, so it is not an unbounded production leak. Tests could bleed only if a
test strands an acquired token; the release/error assertions can prevent that. The unresolved
problem is state publication to remounted consumers, as recorded in R4-F3.

The drag/file-drop isolation contract is coherent: dnd-kit uses pointer/keyboard sensors while the
existing drop zone uses native file-drag events, and AC-49.19/49.28 exercise both directions. The
announcement contract is also source-backed: dnd-kit documents all drag lifecycle announcements,
recommends position rather than index wording, and requires a focusable activator with keyboard
operation ([dnd-kit accessibility guide](https://dndkit.com/legacy/guides/accessibility/)). WCAG
2.2 SC 2.5.7 separately requires a non-drag single-pointer alternative, which the kebab path
provides; keyboard alone would not be sufficient ([W3C Understanding 2.5.7](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements)). The 38 ACs are extensive but coherent for the
cross-input and race surface; the count itself is not an execution blocker.

### G37 / OQ-5 Recommendation to the Human

The manifest fact is true: there is no `@testing-library/*` dependency. The 54-file usage claim is
not: an exact census found 54 unit test files, only 5 importing
`tests/unit/helpers/user-event.ts`, and 49 not importing it
(`C:/Temp/av-kit/r4-review-unit-helper-count.txt`). The helper exports direct methods, not
`userEvent.setup()`. Testing Library's documented API creates a per-test user-event instance with
`userEvent.setup()` ([Testing Library setup documentation](https://testing-library.com/docs/user-event/setup/)); the local helper is an analogous utility, not that API.

My recommendation is to separate two decisions:

1. MEU-49 should use the real package for its new click/keyboard tests if literal G37 compliance is
   desired. That does not require rewriting all 54 files.
2. Deleting the legacy helper and migrating its five current consumers plus other direct-event
   sites is package-wide cleanup and belongs in a separately registered follow-up MEU.

If the human instead chooses the local helper for MEU-49, that is a legitimate bounded decision,
but it is an exception to the literal rule and must be recorded as such. `Local Canon` cannot grant
it by itself.

### Census Verification

The reviewer rerun at `C:/Temp/av-kit/r4/reviewer-census/` reproduced **64 values, 128 variants,
583 hits, S6 0 findings, exit 0**. Both the submitted and reviewer directories contain 194 files;
all 194 corresponding receipts have identical line counts, and both consolidated indexes contain
973 lines (`C:/Temp/av-kit/r4-review-census-compare.txt`). `Invoke-Sweep` redirects raw `rg` output
straight to each receipt; no `head`, `Select-Object -First`, or `tee` truncator is in the sweep path.

All ten survivor dispositions at lines 646–661 of this rolling file are honest. `MEU-56` is live
only where it refers to shared `ProgressBar` inheritance; the other survivors are historical
correction-table quotations or live prohibitions naming the rejected form. The missed RTK prefix is
fixed at `implementation-plan.md:490`; the plan/task header claims are qualified; and `BUILD_PLAN`,
`FAIL_TO_PASS`, and `VITEST_EXIT` resolve through `INHERITED_NAMES.non_set_token_list`
(`named-sets.json:16-21`). R3-F7 is closed.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | Fail | Row 3 topology contradicts its oracle; AC-49.38 has no matching menu deliverable. |
| PR-2 Not-started confirmation | Pass | No MEU-49 dnd module, dependency, test-id, or test exists. Prior MEU-45–47 changes remain in the working tree. |
| PR-3 Task contract completeness | Fail | Rows have the required columns, but the `QueueCardMenu.tsx` change required by AC-49.38 is absent from row 8 and the deliverable list. |
| PR-4 Validation realism | Fail | Red and BuildPlanAudit have demonstrated impossible/false-pass shapes. |
| PR-5 Source-backed planning | Fail | G37's scope exception is labelled as observed local state without the required human decision. |
| PR-6 Handoff/corrections readiness | Pass | Full untruncated census and per-line survivor dispositions were independently reproduced. |
| PR-7 Scope discipline | Fail | OQ-5 is a proposed future registration, not a concrete MEU-ID-backed deferral. |
| PR-8 Control reachability/totality | Fail | R4-F1–F4 trace the Red, feedback, and phase-exit controls to concrete dead ends. |
| PR-9 Single-statement discipline | Pass with note | S6 resolves every live NAME; the preservation-AC prose mislabels the meanings of AC-49.11/.14/.23, but the set membership is correct and this is clerical. |
| DR-1 Claim-to-state match | Fail | Correction claims overstate R3-F1/F2/F3/F6 closure. |
| DR-2 Residual old terms | Pass | All ten survivors were dispositioned and checked. |
| DR-3 Downstream references | Fail | The phase-exit validator is not bound to the downstream `Next:` field. |
| DR-4 Verification robustness | Fail | Exact counterexamples reproduce the Red failure and BUILD_PLAN false-pass. |
| DR-5 Evidence auditability | Pass | Commands, receipts, shipped probe, census index, and live gate outputs are reproducible. |
| DR-6 Cross-reference integrity | Fail | G37, TESTING_LIBRARY_ADOPTION, task row 3, and OQ-5 do not agree with the observed helper census. |
| DR-7 Evidence freshness | Pass | 439 Vitest, 73 Playwright-listed, 509 pytest, 64/128/583 census, and all self-test counts reproduced. |
| DR-8 Completion vs residual risk | Pass | The submission says no implementation has started and does not claim execution completion. |

### Verdict

`changes_required` — R4-F1, R4-F2, and R4-F3 are evidence-backed High findings: the planned Red
sequence is impossible under its own oracle, two core new regression tests can be omitted without
detection, and the single-flight feedback contract cannot be implemented across remount or in the
existing menu surface as scoped. R4-F4 is an additional demonstrated false-pass; R4-F5 requires the
human's explicit G37 decision. The correct collection-shape experiment and the substantially
improved gate/census work do not cure those execution blockers.

### Follow-up Actions

1. Repair the Red ownership/oracle mapping and add AC-49.37/.38 to the enforced Red set; rerun the
   exact planned topology, not a redistributed synthetic topology.
2. Add a reactive queue-held contract and explicitly scope/test `QueueCardMenu` transient disabled
   behavior without violating its structural absence rule.
3. Bind `BuildPlanAudit` to the actual `Next:` line and add the concrete false-pass fixture.
4. Obtain the human's G37/OQ-5 decision, correct the 54-file claim, and use a real MEU ID for any
   package-wide deferral.
5. Rerun the full correction census and independent plan review. Because the human lifted the cap
   only for Round 4, this `changes_required` verdict is a new HARD STOP; do not begin implementation
   without another explicit human direction.

---

## Errata — implementor, 2026-09-04 (post Round 4 verdict)

R4-F5 is correct and the error is mine. The Round 4 corrections section above, in the R3-F3 row
and again under *Open question carried to the human (OQ-5)*, states that **all 54** existing unit
test files use `ui/tests/unit/helpers/user-event.ts`. They do not. Measured:

```text
$ ls -1 ui/tests/unit/*.test.ts* | wc -l
54
$ grep -rl "helpers/user-event" ui/tests/unit/*.test.ts* | wc -l
5
```

The five are `bulk-action-bar`, `queue-card`, `queue-list`, `queue-primitives` and
`queue-toolbar`. The other 49 do not import the helper at all.

This matters because the false number was the whole load-bearing argument for deferring G37
adoption: I claimed adoption would touch all 54 files and therefore could not fit inside MEU-49.
At 5 consumers that argument does not hold, and the reviewer’s split — literal
`@testing-library/user-event` for MEU-49’s own new interaction tests, with the legacy migration
as a separately registered MEU — is not blocked by blast radius. The recommendation I gave
the human was built on a number I did not verify before asserting it.

No plan artifact has been edited in response to this or to any other Round 4 finding. The Round 4
`changes_required` verdict is a HARD STOP and the human authorized only Round 4.

---

## Corrections Applied — Round 5 (implementor, 2026-09-04)

**Authorization:** the human's chat message *"continue until approved: keep reviewer on track for
the intent of the plan, stir away from fixes on fixes. G37 / OQ-5 — No splits, web search and find
out what would be the most optimal approach by way of what others have done in similar situation.
There is no legacy, everything is net new, if the code needs to be replaced it can simply be
removed and recoded into better shape."* (`USER_EXPLICIT`, 2026-09-04). This lifts the Round 4
`PLAN_REVIEW_ROUND_CAP` HARD STOP and standing-authorizes further rounds until `approved`. It also
decides OQ-5 directly: **no split**, resolve in-MEU. No implementation has started — the `ui/` tree
is still unmodified.

### R4-F1 … R4-F5 resolution

| Finding | Resolution | Evidence |
|---|---|---|
| **R4-F1** The Red oracle is *still* unsatisfiable: clause (e) demands every `RED_PHASE_REQUIRED_ACS` id appear in a **failing test name**, but eight of them (AC-49.3–49.7, AC-49.16, AC-49.17, AC-49.31) are owned by `RED_PHASE_UNCOLLECTED_FILES` entries, which report zero `assertionResults` by construction | Clause (e) is now **scoped by derivation**, not by hand-list. New `RED_PHASE_AC_OWNERSHIP` maps each `RED_PHASE_TEST_FILES` entry to the AC ids task row 3 assigns it; `Get-ClauseEIds` returns the ids owned by at least one file expected to **collect**. The eight are proven by the stronger clause **(b2)** instead — a whole file failing for its own missing specifier proves the module under test does not exist yet, which is a *stronger* Red fact than one failing assertion. The derivation re-partitions itself automatically when an AC moves between files. If it ever returns the empty set the oracle **fails** rather than passing inertly | `named-sets.json` `RED_PHASE_AC_OWNERSHIP`, `assert-red-phase.ps1` `Get-ClauseEIds` + clause (e), self-test **cases 15/16** |
| — *proof, not assertion* | Case 10 feeds the **real declared topology** (the fixture builder now emits each id in the file that actually owns it, instead of the round-robin spread that silently relocated the eight and made case 10 prove satisfiability for a plan nobody wrote) and must PASS. Case 15 feeds the **same fixture with ownership disabled** and must FAIL on clause (e) — i.e. it reproduces the round-4 defect on demand. The pair is what makes case 10 evidence: without case 15, a future edit that quietly widened the oracle would still show green | `assert-red-phase.ps1` cases 10 / 15, receipt `C:/Temp/av-kit/r5/red-selftest.txt` |
| **R4-F2** AC-49.37 and AC-49.38 were introduced in round 4 as full ACs but never added to `RED_PHASE_REQUIRED_ACS`, so the Red gate could not see them | Both registered; `RED_PHASE_REQUIRED_ACS` is 24 → **27** (AC-49.37, AC-49.38 and the new AC-49.39). The generic fix matters more than the two ids: the census now asserts the **ownership union is exactly** required + preservation in **both directions**, and that an owned id appears in the file that owns it (placement, not merely presence). An unregistered AC is now structurally impossible rather than fixed once. Self-test case 17 replays the same assertion so `-SelfTest` alone catches it without a checked-out tree | `named-sets.json` `RED_PHASE_REQUIRED_ACS` / `RED_PHASE_AC_OWNERSHIP`, `assert-red-phase.ps1` census + case 17, `task.md` row 3 |
| **R4-F3** The single-flight registry has no reactive surface, so AC-49.35/49.38's "held ⇒ disabled" cannot actually render; and AC-49.38 demanded all four kebab items render `disabled`, which contradicts `QueueCardMenu.tsx` rule 1 and is unsatisfiable on a boundary row | Two halves. (1) `REORDER_SINGLE_FLIGHT_RULE` gains `isQueueReorderHeld(key)`, `subscribeQueueReorder(key, listener)` and a `useQueueReorderHeld(key)` hook over `useSyncExternalStore` — a module-level store the components can actually subscribe to, and one that survives remount. (2) AC-49.38 is restated for items that are **present**, asserted on **two** cards: a middle card (all four disabled) and a first card (exactly `Move down` / `Move to bottom` present and disabled, `Move up` / `Move to top` **absent**). `QueueCardMenu.tsx` gains `disabled?: boolean` on its item model so *temporarily* unavailable renders `disabled` while *structurally* unavailable stays absent — the two rules no longer collide. `task.md` row 8's round-4 sentence was rewritten to match; it was the second site | `named-sets.json` `REORDER_SINGLE_FLIGHT_RULE` / `REORDER_FEEDBACK_TIER`, `implementation-plan.md:296` (AC-49.38), §5 file list (+`QueueCardMenu.tsx`, `QueueCard.tsx`, `QueueList.tsx`), `task.md` row 8 |
| **R4-F4** `Test-BuildPlanAudit` applied `-notmatch` to the **whole** `docs/BUILD_PLAN.md`, so the audit passed on adjacent text: `Phase 11` occurs 4× and `MEU-50` 2× for unrelated reasons while the `Next:` pointer itself stays stale | New `BUILD_PLAN_NEXT_POINTER` declares the segment delimiters plus `must_match` / `must_not_match`. The gate extracts the `Next:` **segment** first and asserts both directions on it. Negative fixture `BuildPlanAudit/next-decoy` reproduces the exact shape — a body carrying `Phase 11` and `MEU-50` elsewhere with a stale pointer — and must fail; the round-4 predicate passes on it | `named-sets.json` `BUILD_PLAN_NEXT_POINTER`, `assert-plan-gates.ps1` `Test-BuildPlanAudit` + fixture `buildplan-next-decoy` |
| **R4-F5** The G37 waiver rests on a false count (see Errata above) and OQ-5 defers the fix | **Resolved in-MEU by human direction — no split, no deferral, no exception.** `TESTING_LIBRARY_ADOPTION` is now an in-MEU deliverable labelled `Human-approved`, new **task row 2a** deletes `ui/tests/unit/helpers/user-event.ts` outright and recodes the 14 `TL_MIGRATION_FILES` onto `render`/`screen` + `userEvent.setup()`, and new **AC-49.39** gates the outcome. The `@testing-library/user-event` Out-of-Scope row is deleted and OQ-5 is **closed**. `G37_RULE` is now met **literally** rather than by intent | `named-sets.json` `TESTING_LIBRARY_PACKAGES` / `TL_MIGRATION_FILES` / `TESTING_LIBRARY_ADOPTION`, `implementation-plan.md` §4A + AC-49.39, `task.md` rows 2 / 2a |

### R4-F5: what the research actually says, and the measured blast radius

The human asked for the optimal approach by way of what others do in the same situation, so this
was researched rather than reasoned from first principles. Three findings decided it:

1. **The standard stack is not one package.** `@testing-library/react@16` moved
   `@testing-library/dom` from a *bundled* dependency to a **peer**, so the canonical install is
   four packages, not two: `@testing-library/react@^16.3.3` + `@testing-library/dom@^10.4.1`
   (explicit peer) + `@testing-library/user-event@^14.6.7` + `@testing-library/jest-dom@^7.0.1`,
   all in **devDependencies**, with `setupFiles` importing `@testing-library/jest-dom/vitest`.
   Installing only `user-event` — the round-4 reviewer's narrower split — is the configuration
   that produces the "multiple versions of @testing-library/dom" failure other projects report.
2. **v14 is the setup form.** Every `userEvent` method is async and awaited, `userEvent.setup()`
   is called per test, and **no** manual `act()` wrapper is added — the library handles it, and a
   stray `act` around an awaited call is the classic double-wrap warning. The local shim is the
   opposite shape (direct calls, hand-wrapped in `act`), which is why keeping it as a re-export
   was rejected: two `userEvent` surfaces in one suite is a fork, not a migration.
3. **The shim's own stated reason has expired.** Its docblock says it exists because
   `ui/package.json` and `ui/package-lock.json` are byte-frozen by `PAGE_ISOLATION_RULE`'s
   `FROZEN_GLOBS`. That was an MEU-45–47 constraint. **MEU-49 already modifies both manifests**
   (task row 2 installs `DND_PACKAGES`), so the justification no longer holds on its own terms.

**Blast radius, measured — and the Errata's number was also not the right one.** 5 files import
the shim; 54 unit files exist in total; **14** use `createRoot`/`act` or simulate interaction, and
that union — not 5 and not 54 — is the real migration scope, registered as `TL_MIGRATION_FILES`.
The other 40 are pure logic and are not touched. Ten of the 14 are new to this MEU's change set;
four were already in it.

**Why in-MEU rather than after.** Row 2a lands **before** the Red phase, so row 3 writes MEU-49's
own new interaction tests on the canonical surface and never on a shim already scheduled for
deletion. Deferring would have meant writing new tests against a surface the very next session
removes — the fixes-on-fixes churn the human's message names directly.

**`G36_RULE` is not relaxed for it.** Row 2a is a mechanical call-site translation: **no assertion
or expected value may change**, and Vitest must report **exactly** `VITEST_BASELINE_COUNT` (439)
before and after — neither above (tests added in a pure-refactor row) nor below (a file stopped
collecting or a case was dropped). That count is the whole proof the translation preserved
behaviour. If a migrated file's assertion fails, the migration is wrong, not the assertion.

### Scope of the round-5 edit, and what did *not* change

`named-sets.json` 94 → **98** keys (`TESTING_LIBRARY_PACKAGES`, `TL_MIGRATION_FILES`,
`RED_PHASE_AC_OWNERSHIP`, `BUILD_PLAN_NEXT_POINTER`); ACs 38 → **39**; estimate ~19 → **~33 files**.
No AC was weakened and no gate was removed. `JSDOM_RECT_RULE` is untouched and still governs what
the new unit tests may assert — `userEvent` does not make jsdom compute layout,
`getBoundingClientRect` is still stubbed to zeros, and a completed dnd-kit drag is still proved in
Playwright. The unit tests exercise `DndContext`'s public interface, which is what the dnd-kit
maintainers themselves recommend for jsdom.

### Verification receipts (all green before dispatch)

```text
PASS: RED_PHASE_ORACLE self-test (17 cases, baseline 439, 27 required-red AC ids,
      3 preservation ACs, 3 expected-uncollected files)     C:/Temp/av-kit/r5/red-selftest.txt
PASS: PLAN_GATE_SCRIPT self-test (60 cases across 8 gates)  C:/Temp/av-kit/r5/gates-selftest.txt
PASS: CORRECTION_CENSUS self-test (11 cases: 5 sweep, 3 universal-claim, 2 inventory,
      1 real-file satisfiability)                           C:/Temp/av-kit/r5/census-selftest.txt
SELFTEST PASS: HANDOFF_AC_CHECK                             C:/Temp/av-kit/r5/acs.txt
SELFTEST PASS: HANDOFF_MARKER_CHECK                         C:/Temp/av-kit/r5/markers.txt
SELFTEST PASS: EXEC_DISPATCH_CHECK                          C:/Temp/av-kit/r5/dispatch.txt
```

Case counts moved with the checks, not ahead of them: RED 14 → **17** (cases 15–17), PLAN_GATE
53 → **60** (5 `Deps` fixtures for the Testing Library obligations, 1 `Deps` fixture for the
shim-importer scan, 1 `BuildPlanAudit/next-decoy`). `-Gate S6` also found two capitalised tokens
the round-5 prose introduced (`PAGE_ISOLATION_RULE`, `USER_EXPLICIT`); both are now registered in
`INHERITED_NAMES`, and the plan header's "Six NAMEs" is now "Seven".

### Live gates on the unstarted tree (both must FAIL, and for the round-5 reasons)

```text
FAIL: PLAN_GATE_SCRIPT Deps (48 problems)              C:/Temp/av-kit/r5/live-deps.txt
  3 DND_PACKAGES undeclared + 4 TESTING_LIBRARY_PACKAGES undeclared in devDependencies,
  7 unresolved in the lockfile, the shim still exists, 5 files still import it,
  and all 14 TL_MIGRATION_FILES lack both the import and userEvent.setup().
FAIL: PLAN_GATE_SCRIPT BuildPlanAudit (8 problems)     C:/Temp/av-kit/r5/live-bpa.txt
  ... docs/BUILD_PLAN.md Next: segment still names MEU-49 - PHASE_EXIT_UPDATES was not
      applied to the pointer -> Next: `p10-queue-card-dnd (MEU-49)`, then Phase 11 sessions 23-26.
```

The second receipt is the R4-F4 proof on the **real** file rather than on a fixture: the segment
extractor bounds the pointer sentence inside `docs/BUILD_PLAN.md:72`'s long paragraph line and
reports it in both directions (missing `MEU-50`, still naming `MEU-49` and `p10-queue-card-dnd`).
The round-4 whole-file predicate passes on that same line, because `Phase 11` occurs 4× and
`MEU-50` 2× elsewhere in the file.

The `Deps` receipt independently confirms the `TL_MIGRATION_FILES` count: 14 distinct files, of
which exactly 5 import the shim — the two numbers the Errata above got wrong in opposite directions.

---
date: 2026-09-04
review_mode: plan
target_plan: docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md
verdict: changes_required
round: 5
findings_count: 3
template_version: "2.1"
requested_verbosity: standard
agent: gpt-5.6-sol (Codex independent reviewer)
---

## Round 5 — Authorized Recheck (2026-09-04)

### Intent Anchor

MEU-49 is meant to add dnd-kit pointer/touch/keyboard reorder to the shared `QueueList`, preserve
Alt+Arrow and the position-appropriate kebab actions as equal paths, keep row drag isolated from
the existing file-drop surface, announce drag state accessibly, and leave the shared component ready
for MEU-55 adoption. The combined Testing Library migration is a human-decided in-MEU prerequisite,
not an open deferral question. The design is close, but the current task cannot be executed exactly
as written and its migration gate can accept the principal recode without that recode occurring.

### Findings

| # | Severity | Confidence | Finding | File:Line | Required correction | Status |
|---|---|---|---|---|---|---|
| R5-F1 | High | High | **R4-F3 is not closed because the task still prohibits the React import that its reactive fix requires.** `REORDER_SINGLE_FLIGHT_RULE` now requires `reorder-single-flight.ts` itself to export `useQueueReorderHeld(key)` implemented with React's `useSyncExternalStore`, and AC-49.35 binds rendered handle state to that hook. Task row 4a simultaneously says the same module “is pure and has no React import.” Following row 4a omits the observable surface and recreates R4-F3; following the named rule violates the executable task. | `named-sets.json:138-139`; `implementation-plan.md:294,327-328`; `task.md:37` | Keep the chosen external-store approach, but make row 4a and its tests describe the reactive exports and permit the required React import (or name a separate hook module consistently in every artifact). Do not leave two incompatible file contracts. | Open |
| R5-F2 | High | High | **Rows 2/2a/3 form an unusable dependency-and-validation sequence.** Row 2 must pass `-Gate Deps`, but `Test-Deps` unconditionally requires the row-2a outcomes: deleted shim, zero shim importers, and every migration file carrying `userEvent.setup()`. Row 2a depends on row 2, so row 2 can never satisfy its own gate at its declared boundary. In the other direction, row 3 says rows 2 and 2a are complete but its `Depends on` cell names only row 2, allowing the Red phase to bypass the migration in the explicit dependency graph. The live gate confirms all row-2a conditions are active, not deferred. | `task.md:32-35`; `assert-plan-gates.ps1:193-315` | Without splitting the MEU, give row 2 a package/lock/guard-only validation, retain the full adoption gate at row 2a, and make row 3 depend on 2a. | Open |
| R5-F3 | High | High | **The new Testing Library gate can pass while the promised React Testing Library migration never happens.** The normative adoption contract and row 2a require replacing `createRoot`/manual `act`/`createElement` mounts with `render`/`screen`, but AC-49.39 and `Test-Deps` check only shim absence plus a `@testing-library/user-event` import and `userEvent.setup()` call. They never require `@testing-library/react`, `render`, or `screen`, and never reject `react-dom/client`/`createRoot` or manual mount `act`. The `Deps/tl-partial-migration` fixture is therefore a lookalike: it fails because the overwritten file lacks user-event, not because it retains `createRoot`. Adding a no-op `userEvent.setup()` to otherwise unchanged hand-rolled files can satisfy both Deps and the exactly-439 count. | `named-sets.json:181`; `implementation-plan.md:297,331-334`; `task.md:33`; `assert-plan-gates.ps1:303-315,936-949` | Make the migration outcome observable: require the RTL import/use expected by the contract and reject the retired manual mount surface in `TL_MIGRATION_FILES`. Change the negative fixture so old-style mounting remains **alongside** valid user-event import/setup and still fails. | Open |

No Critical findings were identified. These are not marginal requests for stricter apparatus: R5-F1
is a contradictory production-module contract, R5-F2 is a never-passing task boundary, and R5-F3 is
a demonstrated false-pass for the principal new Round-5 deliverable.

### R4-F1 … R4-F5 Adjudication

| Finding | Round 5 disposition | Evidence |
|---|---|---|
| R4-F1 | **CLOSED** | The ownership derivation is real scoping. `RED_PHASE_AC_OWNERSHIP` assigns all 30 required/preservation IDs with no symmetric difference (`named-sets.json:614-670`). The derived partition is 19 clause-(e) IDs and exactly eight b2-only IDs. The census requires each b2-only AC title in its owned file and the file to import its registered absent specifier; b2 then requires that exact file/specifier collection failure (`assert-red-phase.ps1:153-163,216-240,303-325`). Case 10 uses the declared ownership topology and passes; case 15 reuses the same `$realGood` report without ownership and fails on (e), reproducing the Round-4 defect rather than a nearby shape (`assert-red-phase.ps1:709-721,778-789`). A missing module does not prove each eventual assertion is correct, but it does prove every owned test is Red because its production subject does not exist; Green and the later AC assertions prove behavior. |
| R4-F2 | **CLOSED** | AC-49.37, AC-49.38, and AC-49.39 are in the 27 required IDs, and the ownership union equals required + preservation in both directions (`named-sets.json:239,614-670`). The independent derived-set receipt found `required=27`, `preservation=3`, `owned=30`, symmetric difference empty. The current omission is fixed and case 17 covers map/set drift (`assert-red-phase.ps1:817-834`). |
| R4-F3 | **NOT CLOSED** | The external-store shape, synchronous publication, boolean snapshot, keyed module lifetime, present-versus-absent menu semantics, and two-card AC-49.38 are conceptually sound (`named-sets.json:139,144`; `implementation-plan.md:294-296`). `QueueCardMenu` can cleanly add `disabled?: boolean` while retaining structural absence (`QueueCardMenu.tsx:165-218,410-423`). However task row 4a's no-React instruction contradicts the required hook; see R5-F1 (`task.md:37`). |
| R4-F4 | **CLOSED** | `BUILD_PLAN_NEXT_POINTER` matches the real one-line paragraph shape (`named-sets.json:673`; `docs/BUILD_PLAN.md:72`). `Test-BuildPlanAudit` finds `Next:`, restricts evaluation to that line, stops at the first `. `, then applies both positive and negative predicates (`assert-plan-gates.ps1:375-468`). On the real file it independently reported missing `MEU-50` and both stale MEU-49 tokens; `BuildPlanAudit/next-decoy` reproduces the adjacent-text false-pass and the 60-case self-test remains satisfiable. |
| R4-F5 | **CLOSED** | OQ-5 is no longer deferred or waived. The human's no-split decision is represented by `TESTING_LIBRARY_ADOPTION`, four registered dev packages, the measured 14-file set, shim deletion, row 2a, and AC-49.39 (`named-sets.json:181,584-612`; `task.md:32-34`). Round 5 introduces separate executability/proof defects in that new work (R5-F2/R5-F3), but it does not revive the rejected split or the false 54-file premise. |

### Testing Library Adoption Review

| Question | Result | Independent evidence |
|---|---|---|
| Package set / versions | **Pass** | Live npm metadata: RTL 16.3.3 peers on React/ReactDOM `^18 || ^19` and `@testing-library/dom ^10`; this tree uses React 19.2 (`ui/package.json:29-30`). user-event 14.6.7 peers on DOM `>=7.21.4`; jest-dom 7.0.1 peers on DOM 10 and Vitest. `@testing-library/dom` is therefore a necessary explicit peer, not redundant. jest-dom's `./vitest` export exists. Its Node `>=22` floor adds no incompatibility because Electron 42.5.0 already requires Node `>=22.12.0`, and the review host is Node 24.19.0. All four belong in devDependencies. Receipts: `round5-npm-rtl.txt`, `round5-npm-dom.txt`, `round5-npm-user-event.txt`, `round5-npm-jest-dom.txt`, `round5-npm-electron.txt`, `round5-npm-jestdom-exports.txt`. |
| Blast radius | **Pass** | Independent `rg -l` found exactly the same 14 files importing `createRoot`/`react-dom/client`; 13 also simulate interaction. The 14th, `use-queue-selection.test.ts`, still owns a hand-rolled React mount and belongs in the RTL mount migration even though it has no current user interaction. There are 54 unit files total and exactly five shim importers. |
| G36 / exactly 439 | **Pass for the count; fail for migration proof** | A fresh live run returned `54 passed`, `439 passed`, exit 0. Mechanical test-surface translation does not legitimately alter Vitest's declared test count, so exactly 439 is attainable and correctly rejects added/dropped cases. It does not prove the mount API changed; that concrete false-pass is R5-F3. |
| Ordering | **Fail** | Row 2's full Deps gate requires row 2a before row 2 can close, while row 2a depends on 2; row 3 depends on 2 instead of 2a (`task.md:32-35`). See R5-F2. |
| Other shim consumers | **Pass** | The only code importers are the five unit files in `TL_MIGRATION_FILES`; no Playwright spec, source file, setup/config file, or other unit file imports it. Documentation/history references are not runtime consumers. |
| MEU size / no-split decision | **Pass with the findings above** | The 14-file migration is package-local, count-preserving prerequisite work and the human explicitly decided it stays in MEU-49. The overall 33-file unit is large but still coherent around one queue-reorder delivery and its canonical test surface. No split is recommended; R5-F1–F3 are in-place contract corrections. |

### Drag / File-Drop / Keyboard Design Review

- `DRAG_STATE_ISOLATION_RULE` is sound: dnd-kit pointer/keyboard sensors wrap rather than replace
  the existing HTML5 file-drop container; the plan keeps `data-drag-state` and the file overlay on
  that inner container and requires them to remain idle/absent through row drag. AC-49.28 exercises
  the real Electron path.
- The exact permutation examples, identity suppression, both page command paths, and persisted
  reload assertion prevent the common post-removal-index and disconnected-page failures.
- The four announcement callbacks, non-empty instructions, title + one-based position strings, and
  dedicated dnd live-region locator cover the accessibility contract without colliding with the
  file-drop `role=status`.
- Kebab and Alt+Arrow remain first-class alternatives and all absolute-permutation paths share one
  queue-keyed synchronous gate. The module-level lifetime and `finally` release are appropriate;
  the remaining defect is the row-4a contradiction in R5-F1, not the external-store approach.
- Phase 11 inheritance remains credible: MEU-55 can adopt the already-optional shared `QueueList`
  reorder surface without duplicating the drag implementation.

No additional substantive drag-design defect was found.

### Independently Run Verification

| Command / check | Exit | Result |
|---|---:|---|
| `assert-red-phase.ps1 -SelfTest` | 0 | PASS — 17 cases; baseline 439; 27 required, 3 preservation, 3 expected-uncollected. |
| `assert-plan-gates.ps1 -SelfTest` | 0 | PASS — 60 cases across 8 gates. The good fixture passes and the package/section/shim/importer/no-setup and Next-decoy negatives emit their expected reasons. The purported old-style-migration fixture does **not** test retained old style; see R5-F3. |
| `run-correction-census.ps1 -SelfTest` | 0 | PASS — 11 cases. |
| `run-correction-census.ps1 -Gate S6` | 0 | `S6: 0 finding(s)`. |
| `assert-plan-gates.ps1 -Gate Deps` on the unstarted tree | 1 | Expected FAIL — 48 problems: 14 missing/unresolved packages, shim + 5 importers, and 28 per-file user-event obligations. This also proves the row-2 sequencing defect because row-2a checks are unconditional. |
| `assert-plan-gates.ps1 -Gate BuildPlanAudit` on the unstarted tree | 1 | Expected FAIL — 8 problems, including the correctly bounded stale `Next:` segment at `docs/BUILD_PLAN.md:72`. |
| `npm --prefix ui run test` | 0 | 54 files / exactly 439 tests passed. Existing React `act` warnings were emitted but no test failed. |
| Live npm registry checks for the four proposed packages + Electron | 0 | Registered versions, peer graph, exports, and Node engine are compatible as described above. |
| Independent file census | 0 | 54 unit files; 14 manual React mounts; 13 interaction files; 5 shim importers; no consumer outside the registered migration files. |

Canonical receipts are under `C:/Temp/av-kit/round5-*.txt`; process exit codes above were captured
immediately after each child command, before receipt reads.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | **Fail** | R5-F1 and R5-F2 are direct named-contract/task and dependency/validation mismatches. |
| PR-2 Not-started confirmation | Pass | Dnd-kit/TL packages and new reorder modules/tests are absent; live Deps/BuildPlanAudit fail in the expected preimplementation state. Existing dirty files are prior Phase 10 work, not MEU-49 implementation. |
| PR-3 Task contract completeness | **Fail** | Every row has the required columns, but rows 2/2a/3 cannot satisfy their declared dependency/validation boundaries and row 4a contradicts its governing deliverable. |
| PR-4 Validation realism | **Fail** | The main migration can false-pass unchanged manual mounts (R5-F3). Red and BuildPlanAudit are otherwise satisfiable and discriminating. |
| PR-5 Source-backed planning | Pass | Drag, accessibility, package, and human-decided no-split rules have explicit Spec/Local Canon/Research-backed/Human-approved bases. |
| PR-6 Correction readiness | Pass | Round-5 correction census and per-hit dispositions are present; all three plan-local self-tests and S6 ran green independently. |
| PR-7 Scope discipline | Pass | OQ-5 is closed in-MEU per human direction; no waiver or orphan deferral remains. |
| PR-8 Control reachability/totality | **Fail** | R5-F1 removes the only specified reactive production surface if row 4a is followed; R5-F3 demonstrates a materially missing deliverable that the gate accepts. |
| PR-9 Single-statement discipline | Pass with blocking contradiction already counted | The named sets are centralized; task row 4a's incompatible no-React sentence is R5-F1 rather than a duplicate clerical finding. |

### Open Questions / Assumptions

None. OQ-5 is human-decided and was not re-litigated. This review assumes the existing
`setupFiles: ['./tests/unit/setup.ts']` may either gain the jest-dom import in that setup file or
add the package export as a second setup entry; either is executable and does not affect the verdict.

### Follow-up Actions

1. Reconcile task row 4a with the chosen `useSyncExternalStore` export so R4-F3 is actually closed.
2. Remove the row-2/2a gate cycle and make row 3 depend on row 2a; keep all work inside MEU-49.
3. Make AC-49.39/Deps prove the promised RTL mount recode, using a negative fixture that retains
   old mounting while satisfying user-event setup.
4. Re-run the same four required script commands plus live Deps/BuildPlanAudit and return for the
   standing-authorized next review round. Do not begin implementation while these contradictions remain.

### Residual Risk

After R5-F1–F3, remaining risk is normal implementation risk: getting pointer coordinates stable in
Electron, propagating queue-held state through the shared list/card without focus regressions, and
keeping the 14-file migration assertion-identical. The plan's exact-order E2E, announcement checks,
file-drop isolation assertion, two-card disabled-state tests, and full-suite gates are proportionate.

### Verdict

`changes_required` — R4-F1, R4-F2, R4-F4, and R4-F5 are closed. R4-F3 remains open because its
reactive hook is forbidden by task row 4a, and the new Testing Library work adds one never-passing
task boundary plus one concrete false-pass that can ship the old mounting surface. These are three
delivery-level High findings. They can be corrected in place without splitting MEU-49 or revisiting
the human's OQ-5 decision.

## Corrections Applied — Round 6 (implementor, 2026-09-04)

**Authorization:** the same standing `USER_EXPLICIT` message quoted in the Round 5 corrections
section — *"continue until approved … stir away from fixes on fixes … No splits … if the code needs
to be replaced it can simply be removed and recoded into better shape."* No implementation has
started; the `ui/` tree is still unmodified.

All three round-5 findings are accepted without argument. Each was a real defect of the *round-5
corrections themselves*, not of the drag design the reviewer separately reviewed and passed. None
was fixed by adding apparatus around the problem; in each case the thing that was wrong was
removed and rewritten.

### R5-F1 … R5-F3 resolution

| Finding | Resolution | Evidence |
|---|---|---|
| **R5-F1** `REORDER_SINGLE_FLIGHT_RULE` required `reorder-single-flight.ts` to export the `useSyncExternalStore` hook while task row 4a said that module has no React import — two file contracts that could not both be followed | Resolved in the direction that keeps the **command layer** React-free, because that is the constraint with a real cause: `download-commands.ts` and `convert-commands.ts` import the gate and have no React import of their own, so a hook living in the store drags React into plain-TS command modules purely so a component can subscribe. The store keeps its four framework-free exports (`createSingleFlight`, `acquireQueueReorder`, `isQueueReorderHeld`, `subscribeQueueReorder`); the hook moves to **new `REORDER_HELD_HOOK`** — `ui/src/renderer/src/lib/queue/use-queue-reorder-held.ts`, a one-line `useSyncExternalStore` binding with a **boolean** snapshot, which is the standard store/hook split and is also what avoids React's "result of getSnapshot should be cached" loop. New **task row 4b** owns it; row 5 now depends on 4b. Every artifact names the same module for the binding — that is the actual fix, since the defect was two artifacts naming different homes for one export | `named-sets.json` `REORDER_HELD_HOOK` (new) + rewritten `REORDER_SINGLE_FLIGHT_RULE`, `implementation-plan.md` §5 file list / AC-49.35 / §2, `task.md` rows 4a (restated, still React-free) and 4b (new) |
| — *why no separate unit file for the hook* | A test that mounted a three-line `useSyncExternalStore` binding in isolation would assert the React API, not this plan's behaviour. It is proved where it is observable: AC-49.35 (a sibling card's acquire disables this card's handle without a remount) and AC-49.38 (present kebab items and Alt+Arrow gated on the same flag) | `named-sets.json` `REORDER_HELD_HOOK.note`, `task.md` row 4b |
| **R5-F2** Row 2 was gated on `-Gate Deps`, which also asserts row 2a's outcomes; row 2a depends on row 2, so row 2 could never pass at its declared boundary. In the other direction row 3's `Depends on` named only row 2, letting the Red phase bypass the migration in the dependency graph | `Test-Deps` gains `-Mode Packages|Full` and the script a `DepsPackages` gate value. Row 2 validates with **`-Gate DepsPackages`**: manifests, lockfile resolution, the rejected packages, and the jest-dom `setupFiles` wiring — everything row 2 actually delivers. Row 2a keeps the **full** `-Gate Deps`. Row 3's `Depends on` is **2 → 2a**. The boundary is now proven in both directions by two paired fixtures, not asserted: `Deps/packages-mode-pre-migration` is the exact tree that exists when row 2 closes and must **PASS** in `Packages` mode, and `Deps/full-mode-pre-migration` is the same tree and must **FAIL** in `Full` mode | `assert-plan-gates.ps1` `Test-Deps -Mode` + `ValidateSet`, self-test cases `packages-mode-pre-migration` / `full-mode-pre-migration`, `task.md` rows 2 / 2a / 3 |
| **R5-F3** The migration gate could not see the migration: AC-49.39 and `Test-Deps` checked only shim absence plus a user-event import and `setup()` call, so a file that kept its `createRoot` mount and gained one no-op `userEvent.setup()` passed both the gate and the exactly-439 count. The `tl-partial-migration` fixture was a lookalike — it failed for a missing import, not for the retained mount | The contract is restated as the two halves it actually has, and the gate is made to *be* that contract rather than a proxy for it. **Mount half, all 14 `TL_MIGRATION_FILES`:** imports `@testing-library/react`, calls `render(`, queries through `screen`, and retains **none** of the retired surface — no `react-dom/client`, no `createRoot`, no `act` imported from `'react'`. **Interaction half, the 13 `TL_INTERACTION_FILES`:** additionally imports `@testing-library/user-event` and calls `userEvent.setup()`. `createElement` is explicitly **allowed** and is not part of the retired surface: these are `.test.ts` files with no JSX, so `render(createElement(C, props))` is the idiomatic RTL form and all 14 files use it today. The lookalike fixture is rewritten so the overwritten file is otherwise valid, and **new `Deps/tl-old-style-retained`** is the reviewer's exact false-pass tree — every round-5 predicate satisfied *plus* `createRoot` — which must now fail on "still imports react-dom/client" | `named-sets.json` `TESTING_LIBRARY_ADOPTION` clauses (a)–(g) + `TL_INTERACTION_FILES` / `TL_MOUNT_ONLY_FILES` (new), `implementation-plan.md` AC-49.39, `task.md` rows 2 / 2a, `assert-plan-gates.ps1` per-file predicate + fixtures `tl-old-style-retained` / `tl-partial-migration` / `tl-no-rtl-import` / `tl-no-setup` |
| — *the mirror defect, avoided deliberately* | The 14th file, `use-queue-selection.test.ts`, mounts but simulates nothing. Demanding `userEvent.setup()` there would have manufactured a dead line purely to satisfy a check — the same class of defect as R5-F3, pointing the other way. It is registered in **`TL_MOUNT_ONLY_FILES`** and exempted from the interaction half only. The exemption cannot be quietly grown: the gate asserts `TL_INTERACTION_FILES` and `TL_MOUNT_ONLY_FILES` **partition** `TL_MIGRATION_FILES` exactly in both directions, with `tl-partition-gap` / `tl-partition-overlap` / `tl-partition-real` covering it | `named-sets.json` `TL_MOUNT_ONLY_FILES.note`, `assert-plan-gates.ps1` `Test-TlPartition` + three partition fixtures |

### What was removed rather than patched

Per the human's standing direction, nothing here is a guard bolted onto a broken thing:

- The round-5 clause putting `useQueueReorderHeld` in `reorder-single-flight.ts` was **deleted**
  from the rule, not softened; the hook has a new home and a new task row.
- The round-5 `Deps` gate was **not** given an escape hatch for row 2. `Test-Deps` was split into
  the two modes the two rows actually need, so both rows are gated on the whole of what they own.
- `Deps/tl-partial-migration` was **rewritten**, not supplemented: as the reviewer found, it passed
  its assertion for the wrong reason, which makes it worse than no fixture.

### Verification

Every plan-local script self-tests green, and the two `Deps` modes were run live on the unstarted
tree to prove they fail for their designed reasons rather than merely existing.

| Command | Result | Receipt |
|---|---|---|
| `assert-plan-gates.ps1 -SelfTest` | **PASS — 69 cases across 8 gates** (60 in round 5; +9 for the two modes, the retired-surface predicate and the partition) | `C:/Temp/av-kit/r6/assert-plan-gates-selftest.txt` |
| `assert-red-phase.ps1 -SelfTest` | PASS — 17 cases, baseline 439, 27 required + 3 preservation, 3 expected-uncollected | `C:/Temp/av-kit/r6/assert-red-phase-selftest.txt` |
| `run-correction-census.ps1 -SelfTest` | PASS — 11 cases | `C:/Temp/av-kit/r6/run-correction-census-selftest.txt` |
| `assert-handoff-markers.ps1` / `assert-handoff-acs.ps1` / `assert-exec-review-dispatch.ps1` `-SelfTest` | PASS (3) | `C:/Temp/av-kit/r6/assert-handoff-*.txt`, `assert-exec-review-dispatch-selftest.txt` |
| `run-correction-census.ps1` (live, Literals + S6) | exit 0 — S6 **0 findings**; 96 values / 193 variants swept; **zero-hit NEW values: (none)** — every round-6 edit landed where it is claimed. Six entries now declare `superseded_by` and are reported separately, which is what the round-5 report was conflating with "the edit did not land" | `C:/Temp/av-kit/census/census-index.txt` |
| `assert-plan-gates.ps1 -Gate DepsPackages` (live) | **FAIL, 15 problems**, exit 1 — 7 packages undeclared, 7 unresolved in the lockfile, jest-dom not wired. Row 2's boundary is now reachable *and* not yet satisfied | `C:/Temp/av-kit/r6/live-DepsPackages.txt` |
| `assert-plan-gates.ps1 -Gate Deps` (live) | **FAIL, 116 problems**, exit 1 — ending on `use-queue-selection.test.ts still calls createRoot` and `still imports act from 'react'`, i.e. the clauses R5-F3 says were missing | `C:/Temp/av-kit/r6/live-Deps.txt` |
| `assert-plan-gates.ps1 -Gate BuildPlanAudit` (live) | FAIL, 8 problems, exit 1 — unchanged, as expected on an unstarted tree | `C:/Temp/av-kit/r6/live-BuildPlanAudit.txt` |

Counts restated by this pass: `named-sets.json` **98 → 101** keys; `PLAN_GATE_SCRIPT` self-test
**60 → 69** cases; estimate **~33 → ~34** files (the new hook module); AC count **unchanged at 39** —
round 6 corrected three contracts and added no criteria.

---
date: 2026-09-04
review_mode: plan
target_plan: docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md
verdict: changes_required
round: 6
findings_count: 1
template_version: "2.1"
requested_verbosity: standard
agent: gpt-5.6-sol (Codex independent reviewer)
---

## Round 6 — Authorized Recheck (2026-09-04)

### Intent Anchor

MEU-49 is meant to add queue-card drag reorder without weakening the existing keyboard, kebab,
file-drop, accessibility, or single-flight behavior, while completing the human-decided in-MEU
Testing Library migration before the new Red tests are written. Round 6 closes the store/hook
contradiction and the retained-manual-mount false pass, but row 2's new boundary gate still accepts
an explicitly required row-2 deliverable as missing.

### Findings

| # | Severity | Confidence | Finding | File:Line | Required correction | Status |
|---|---|---|---|---|---|---|
| R6-F1 | High | High | **`DepsPackages` false-passes a missing `DND_DEP_GUARD_SUPERSESSION`, so R5-F2 is not fully closed.** Row 2 and AC-49.2 require `ui/tests/unit/queue-card.test.ts` to narrow the live `/dnd-kit\|react-virtual/` dependency guard to `/react-virtual/` and add the in-place MEU-49/spec supersession comment. `Test-Deps -Mode Packages` checks the two manifests, lock resolution, rejected packages, and jest-dom wiring, then returns without reading `queue-card.test.ts`. Its claimed exact-boundary fixture overwrites every `TL_MIGRATION_FILES` entry — including `queue-card.test.ts` — with four generic pre-migration lines that contain no dependency guard at all, yet asserts that Packages mode passes. An independent invocation of the actual functions reproduced the false pass: `packages-mode-problems=0` while `fixture-has-required-narrow-guard=False`. On the real unstarted tree, the old blocking guard is still present. This violates PR-4: row 2 can be marked complete while one of its two owned ACs and named deliverables did not land. | `implementation-plan.md:110,124`; `task.md:32`; `assert-plan-gates.ps1:243-346,1142-1154`; `ui/tests/unit/queue-card.test.ts:799-807` | Keep the two-mode design and no-split decision. Make Packages mode assert the narrowed `/react-virtual/` guard plus the required supersession comment/spec citation, and make the pre-migration boundary fixture model that row-2 result instead of deleting the guard from its synthetic `queue-card.test.ts`; add a negative case for the live broad guard or a missing supersession. | Open |

No Critical findings were identified. This is not a request for a marginally stricter predicate:
the missing check is the named AC-49.2 production-test change row 2 itself owns, and the existing
fixture proves the gate passes when that deliverable is absent.

### R5-F1 … R5-F3 Adjudication

| Finding | Round 6 disposition | Evidence |
|---|---|---|
| R5-F1 | **CLOSED** | The contradiction is gone. `REORDER_SINGLE_FLIGHT_RULE` assigns exactly four framework-free store exports and moves the only React binding to `REORDER_HELD_HOOK`; the new named contract fixes that hook at `ui/src/renderer/src/lib/queue/use-queue-reorder-held.ts` (`named-sets.json:138-141,690-693`). The plan's file inventory and AC-49.35 name the same module (`implementation-plan.md:179-180,295`), while task rows 4a/4b separate the store and hook and row 5 depends on 4b (`task.md:37-39`). A direct import census confirms `download-commands.ts:1-13` and `convert-commands.ts:1-25` have no React import. The hook shape returns a primitive boolean snapshot, consumes the store's unsubscribe-returning `subscribeQueueReorder`, and the store contract requires synchronous listener publication on acquire/release. AC-49.35 proves a sibling acquire updates a mounted card without remount; AC-49.38 proves the rendered affordances update on hold/release. Together with the exact hook implementation and AC-49.37's module-lifetime remount case, a separate unit file is not required. |
| R5-F2 | **NOT CLOSED** | The cycle itself is repaired: row 2 uses `DepsPackages`, row 2a uses full `Deps`, and row 3 depends on 2a (`task.md:32-34`; `assert-plan-gates.ps1:233-346,1435-1440`). The complete dependency extraction is linear and acyclic: `1 -> 2 -> 2a -> 3 -> 3a -> 4 -> 4a -> 4b -> 5` and then sequentially through H2-5. Packages mode requires nothing produced only by row 2a. However it omits the row-2 guard change and its paired fixture is not the row-2 tree; see R6-F1. |
| R5-F3 | **CLOSED** | The exact Round-5 false-pass no longer works. All 14 files owe the mount predicates and retired-surface rejections; the 13 registered interaction files also owe the user-event import/setup predicates (`assert-plan-gates.ps1:348-421`). The actual `tl-old-style-retained` tree satisfies the prior positive predicates and retains `createRoot`; an independent direct invocation returned exactly three errors — retained `react-dom/client`, `createRoot`, and `act` from React — so it fails for the intended retained-mount reason (`assert-plan-gates.ps1:1089-1110`). The good fixture proves `createElement` is allowed, and an RTL `act` import remains allowed; rejecting `act` specifically from React is executable because RTL re-exports it. The current named membership is principled: 13 measured interaction files and the single mount-only `use-queue-selection.test.ts` (`named-sets.json:695-719`). `Test-TlPartition` prevents gaps, overlaps, and names outside `TL_MIGRATION_FILES` (`assert-plan-gates.ps1:198-230`). It does not make membership tamper-proof — moving one current interaction file to the mount-only set produced zero partition problems — but that would be an overt edit to the reviewed 13/1 named contract and contradict task row 2a, not a false pass against this fixed plan. No execution row authorizes such a plan-artifact rewrite. |

### Round-6 Regression Checks

| Surface | Result | Evidence |
|---|---|---|
| Task dependency chain | **Pass** | Direct table extraction found every dependency points backward and the chain is linear, including `2 -> 2a -> 3`, `4a -> 4b -> 5`, H1-6a -> H1-7, and H1-7 -> H2-1. No cycle or forward dependency was introduced. |
| AC-49.39 coverage | **Pass** | The rewritten AC still requires shim deletion, zero shim importers, all four registered Testing Library packages in devDependencies at their registered ranges, the 14-file mount migration, and the 13-file interaction migration (`implementation-plan.md:298`; `named-sets.json:584-612,695-719`). AC-49.39 remains in `RED_PHASE_REQUIRED_ACS` and in the downloader behavior ownership entry (`named-sets.json:208-239,645-657`); the untouched Red oracle's 17-case self-test passes. |
| Correction census `superseded_by` | **Pass** | Non-superseded zero-hit `new` values remain selected by the original missing-edit report (`run-correction-census.ps1:667-670`). Only entries with a nonempty `SupersededBy` move to the separate report (`:672-677`), so the change does not weaken the zero-hit treatment for ordinary entries. S6 still alone controls gate exit (`:612-615,687-688`). |
| R5-F1 store justification | **Pass** | The live command-module import list contains no React or `react-dom/client` import. Keeping the shared mutation gate framework-free is true on disk. |

### Independently Run Verification

All commands used `rtk proxy`, redirected all streams to `C:/Temp/av-kit/`, captured
`$LASTEXITCODE` immediately after the child process, and only then read the receipt.

| Command / check | Exit | Result |
|---|---:|---|
| `assert-plan-gates.ps1 -SelfTest` | 0 | PASS — 69 cases across 8 gate groups. |
| `assert-red-phase.ps1 -SelfTest` | 0 | PASS — 17 cases; baseline 439; 27 required-red, 3 preservation, 3 expected-uncollected. |
| `run-correction-census.ps1 -SelfTest` | 0 | PASS — 11 cases. |
| `run-correction-census.ps1 -Gate S6` | 0 | PASS — `S6: 0 finding(s)`. |
| `assert-plan-gates.ps1 -Gate DepsPackages` on the unstarted tree | 1 | Expected FAIL — exactly 15 problems: seven missing manifest declarations, seven unresolved lock entries, and missing jest-dom wiring. It reports nothing about the still-broad dependency guard. |
| `assert-plan-gates.ps1 -Gate Deps` on the unstarted tree | 1 | Expected FAIL — exactly 116 problems, including retained `react-dom/client`, `createRoot`, and React `act`. |
| Direct actual-function R5-F3 retained-mount probe | 0 | Probe succeeded: the adversarial tree produced 3 gate problems, all on the retained manual-mount surface; `retained-surface-reason-count=1`. Receipt: `C:/Temp/av-kit/r6-f3-adversarial.txt`. |
| Direct actual-function partition reclassification probe | 0 | Moving `app-shell-wiring.test.ts` from interaction to mount-only in memory produced `reclassified-partition-problems=0`; disposition is recorded above and is non-blocking for the fixed on-disk contract. Same receipt. |
| Direct actual-function row-2 boundary probe | 0 | `Test-Deps -Mode Packages` returned `packages-mode-problems=0` while the fixture reported `fixture-has-required-narrow-guard=False`. Receipt: `C:/Temp/av-kit/r6-f2-boundary-probe.txt`. |
| Command-module React import census | 0 | Imports were enumerated in both files; neither imports React. Receipt: `C:/Temp/av-kit/r6-command-imports.txt`. |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | **Fail at row-2 gate** | Plan and task agree that the dependency guard is a row-2 deliverable, but its declared `DepsPackages` implementation does not enforce it (R6-F1). The remaining Round-6 contracts align. |
| PR-2 Not-started confirmation | Pass | All task rows remain unchecked; the live package gates fail in the expected preimplementation state; the new store/hook modules are absent. Existing dirty UI files are prior Phase 10 work, as already established in Round 5. |
| PR-3 Task contract completeness | Pass | Every actionable row retains owner, deliverable, validation, dependency, context strategy, durable output, model, and status; the defect is validation realism, not a missing table field. |
| PR-4 Validation realism | **Fail** | R6-F1 is a concrete false pass for an AC-49.2 deliverable. The retained-mount false pass is closed. |
| PR-5 Source-backed planning | Pass | The Round-6 store/hook split and Testing Library contract remain source-backed; OQ-5 stays human-decided. |
| PR-6 Correction readiness | Pass | The Round-6 correction log, receipts, and per-finding dispositions are present; all three self-tests and S6 reproduce. |
| PR-7 Scope discipline | Pass | No split is proposed or needed; the no-split decision is not re-opened. |
| PR-8 Control reachability/totality | **Fail** | The row-2 boundary can report green with its required guard supersession absent (R6-F1). The hook and migration controls are otherwise reachable and discriminating. |
| PR-9 Single-statement discipline | Pass with clerical note | The executable mode mapping is clear in task/script. `PLAN_GATE_SCRIPT.gates.Deps` still describes the older row-2-only package surface (`named-sets.json:246-259`), but the task and switch unambiguously govern execution; this clerical stale description does not add a finding. |

### Open Questions / Assumptions

None. OQ-5 remains human-decided and was not re-litigated. The review assumes plan artifacts remain
immutable during execution except through an explicit plan-corrections cycle; the task contains no
row authorizing a builder to reclassify `TL_INTERACTION_FILES` or `TL_MOUNT_ONLY_FILES`.

### Follow-up Actions

1. Close R6-F1 in place by adding the AC-49.2 dependency-guard/supersession assertion to Packages
   mode and replacing the lookalike row-2 fixture with the actual boundary shape plus one negative.
2. Re-run the same six required commands and return only for that focused recheck. Do not split the
   MEU and do not alter the already-closed store/hook or Testing Library mount contracts.

### Residual Risk

After R6-F1, the remaining risk is ordinary implementation risk in Electron drag coordinates,
external-store wiring across route remounts, and assertion-identical migration of the 14 test files.
The current Round-6 hook and migration predicates are proportionate to those contracts.

### Verdict

`changes_required` — R5-F1 and R5-F3 are closed, and R5-F2's cycle/dependency correction works, but
R5-F2 is not fully closed because `DepsPackages` accepts the required row-2 dependency-guard
supersession as absent. The one demonstrated false pass is delivery-level and must be fixed before
implementation; no settled Round-5 pass or human no-split decision was re-opened.

## Corrections Applied — Round 7 (implementor, 2026-09-04)

**Authorization:** the same standing `USER_EXPLICIT` message quoted in the Round 5 and Round 6
corrections sections — *"continue until approved … stir away from fixes on fixes … No splits … if
the code needs to be replaced it can simply be removed and recoded into better shape."* No
implementation has started; the `ui/` tree is still unmodified.

R6-F1 is accepted without argument. The reviewer is right, and the finding is the same class of
defect as R5-F3 one level down: a gate that named a deliverable in prose and asserted a proxy for
it. Round 6 split `Test-Deps` into the two modes the two rows own — and then wrote the row-2 mode
without the one check row 2 uniquely owns. Worse, the fixture offered as proof of the boundary
deleted the guard from its synthetic `queue-card.test.ts` and still asserted a PASS, so the
apparatus was actively certifying the false pass rather than merely missing it.

### R6-F1 resolution

| Aspect | Resolution | Evidence |
|---|---|---|
| **The missing check** | `DND_DEP_GUARD_SUPERSESSION` existed only as prose. It now has an executable twin, **`DND_DEP_GUARD_CHECK`**, whose every field is a **literal substring, never a regex**: `retired` (`/dnd-kit\|react-virtual/`) must be **absent**; `narrowed` (`/react-virtual/.test(name)`) and `armed` (`.toEqual([])`) must be **present**; and a comment within `comment_window` lines of the narrowed assertion must carry both `MEU-49` and `10-queue-card-ui.md:254-256`. `Test-DepGuard` reads it and `Test-Deps` calls it | `named-sets.json` `DND_DEP_GUARD_CHECK` (new, key 102), `assert-plan-gates.ps1` `Test-DepGuard` |
| **Which mode it runs in** | **Both.** Row 2, not row 2a, owns AC-49.2, so the call sits *above* the `if ($Mode -ne 'Full') { return }` line rather than in the adoption half. A `Packages`-mode green with the broad guard still in place is a false pass on the very row being gated | `assert-plan-gates.ps1` `Test-Deps` — `Test-DepGuard` invoked before the mode return |
| **"In place" made executable** | The named contract says *in-place* supersession comment, and the MEU-45 precedent it cites sits **6** lines from the assertion it supersedes. A 12-line window makes that a predicate instead of an adjective: a comment parked at the top of a 900-line file does not satisfy it. Only `//`, `*` and `/*` lines count, so a matching string inside code cannot pass for a comment | `named-sets.json` `comment_window: 12`, fixture `Deps/dep-guard-comment-not-in-place` |
| **The lookalike fixture** | `Deps/packages-mode-pre-migration` no longer overwrites the guard file with generic pre-migration lines. It now models what row 2 **actually delivers**: the pre-migration mount surface *plus* the narrowed guard, since row 2a — the only row this tree leaves undone — is not the row that touches the guard. The same helper (`Add-DepGuard`) applies to `New-GoodTree`, so the rule is stated once and the good tree cannot fall behind it | `assert-plan-gates.ps1` `Add-DepGuard`, `$depGuardBlock`, `New-GoodTree`, fixture `deps-pre-migration` |
| **Four negatives, not one** | A single negative would have covered the reviewer's tree and nothing else. The change can be absent in four distinguishable ways and each has its own case: **(i)** `Deps/dep-guard-still-broad` — nobody touched it, which is the tree that exists the moment `DND_PACKAGES` lands and in which the whole unit suite fails on a pre-existing assertion; **(ii)** `Deps/dep-guard-deleted` — narrowing replaced by outright deletion, the `G36_RULE` violation the contract's own note names, and specifically *not* catchable by (i) since it removes the broad regex too; **(iii)** `Deps/dep-guard-no-supersession` — narrowed correctly, no stated reason, which is indistinguishable from quiet test-weakening; **(iv)** `Deps/dep-guard-comment-not-in-place` — the comment exists but 30 lines away | `assert-plan-gates.ps1` self-test, 69 → **73** cases |

### The reviewer's clerical note, taken

PR-9 flagged that `PLAN_GATE_SCRIPT.gates.Deps` still described the round-2 row-2-only package
surface. It is rewritten to describe both modes and what each one owns, including the new guard
assertion — the same key was being edited anyway, and a stale description of the gate that just
false-passed is not worth carrying forward.

### Verification

| Command | Result | Receipt |
|---|---|---|
| `assert-plan-gates.ps1 -SelfTest` | **PASS — 73 cases across 8 gates** (69 in round 6; +4 for the four shapes of a missing AC-49.2) | `C:/Temp/av-kit/r7/selftest.txt` |
| `assert-red-phase.ps1 -SelfTest` | PASS — 17 cases (untouched by round 7, re-run because `named-sets.json` changed) | `C:/Temp/av-kit/r7/assert-red-phase-selftest.txt` |
| `run-correction-census.ps1 -SelfTest` | PASS — 11 cases | `C:/Temp/av-kit/r7/census-selftest.txt` |
| `assert-handoff-markers.ps1` / `assert-handoff-acs.ps1` / `assert-exec-review-dispatch.ps1` `-SelfTest` | PASS (3) | `C:/Temp/av-kit/r7/assert-handoff-*.txt`, `assert-exec-review-dispatch-selftest.txt` |
| `run-correction-census.ps1` (live) | exit 0 — **zero-hit NEW values: (none)**, so every round-7 edit landed where it is claimed; seven superseded entries all `gone as expected`, now including `[C10 -> C13] "now **69** cases"` | `C:/Temp/av-kit/r7/census-full.txt` |
| `run-correction-census.ps1 -Gate S6` | exit 0 — **0 findings** | `C:/Temp/av-kit/r7/census-live.txt` |
| `assert-plan-gates.ps1 -Gate DepsPackages` (live) | **FAIL, 16 problems** (15 in round 6), exit 1 — the new 16th is `ui/tests/unit/queue-card.test.ts still asserts the broad /dnd-kit\|react-virtual/ dependency guard`. This is R6-F1 reproduced by the fixed gate on the real tree | `C:/Temp/av-kit/r7/live-DepsPackages.txt` |
| `assert-plan-gates.ps1 -Gate Deps` (live) | **FAIL, 117 problems** (116 in round 6), exit 1 — the same guard problem plus the unchanged adoption half | `C:/Temp/av-kit/r7/live-Deps.txt` |
| `assert-plan-gates.ps1 -Gate BuildPlanAudit` (live) | FAIL, 8 problems, exit 1 — unchanged, as expected on an unstarted tree | `C:/Temp/av-kit/r7/live-BuildPlanAudit.txt` |

Counts restated by this pass: `named-sets.json` **101 → 102** keys (`DND_DEP_GUARD_CHECK`);
`PLAN_GATE_SCRIPT` self-test **69 → 73** cases; AC count **unchanged at 39** and the file estimate
**unchanged at ~34** — round 7 added one contract and four fixtures, and no criteria or files.

---
date: 2026-09-04
review_mode: plan
target_plan: docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md
verdict: approved
round: 7
findings_count: 0
template_version: "2.1"
requested_verbosity: standard
agent: gpt-5.6-sol (Codex independent reviewer)
---

## Round 7 — Focused R6-F1 Closure Review (2026-09-04)

### Intent Anchor

MEU-49 is meant to add queue-card drag reorder without weakening the existing keyboard, kebab,
file-drop, accessibility, or single-flight behavior, while completing the human-decided in-MEU
Testing Library migration before the new Red tests are written. Round 7 asks only whether row 2's
Packages gate now rejects a missing AC-49.2 guard supersession without damaging the two-mode
dependency boundary. It does.

### Findings

None. No Critical, High, Medium, or Low findings were identified in the Round-7 correction.

### R6-F1 Adjudication

| Finding | Round 7 disposition | Evidence |
|---|---|---|
| R6-F1 | **CLOSED** | `Test-DepGuard` now reads the registered file and rejects the retired broad guard, a deleted/nonnarrowed assertion, an unarmed narrowed guard, and an absent or out-of-window marker/citation (`assert-plan-gates.ps1:263-312`). `Test-Deps` invokes it before the Packages-mode return, so both modes execute it (`:425-432`). The direct Round-6-equivalent tree — packages installed, jest-dom wired, row 2a still pre-migration, live broad guard copied untouched — now returned **1** problem, specifically `still asserts the broad /dnd-kit|react-virtual/ dependency guard`, rather than Round 6's zero. Receipt: `C:/Temp/av-kit/r7-review-direct-functions.txt`. |

### Focused Attack Results

| Attack | Result | Evidence |
|---|---|---|
| (a) Re-run the Round-6 false pass | **Rejected correctly.** `attack-fixture-has-required-narrow-guard=False`, the broad literal was present, and actual `Test-Deps -Mode Packages` returned the one broad-guard problem. The live Packages gate independently reports the same problem as its 16th failure. | `assert-plan-gates.ps1:274-276,425-432`; `C:/Temp/av-kit/r7-review-direct-functions.txt`; `C:/Temp/av-kit/r7-review-live-depspackages.txt` |
| (b) Exact row-2 boundary | **Correct.** The synthetic `deps-pre-migration` guard file contains the narrowed literal and not the retired one. Packages mode returned 0. Full mode returned 111 row-2a problems, including the retained shim and `createRoot`, with **no guard problem**. `Add-DepGuard` is used for both good-tree migration-file branches and for every boundary migration-file write (`assert-plan-gates.ps1:252-256,939-956,1233-1248`). | `C:/Temp/av-kit/r7-review-direct-functions.txt`; self-test cases at `assert-plan-gates.ps1:1249-1250` |
| (c) Four negatives | **All reject their intended defect shapes.** Broad: 1 retired-guard problem. Deleted: 1 missing-narrowed-assertion problem and **not** the broad clause. No supersession: missing in-window marker and citation. Comment 30 lines away: the same two *in-place* contract errors because the marker/citation are outside the 12-line scan. The latter two deliberately converge on the same contract clause, but the far-comment fixture uniquely exercises the window; none false-passes. | `assert-plan-gates.ps1:1252-1316`; `C:/Temp/av-kit/r7-review-direct-functions.txt` |
| (d) Predicate against the real file | **Accepts the intended edit.** On a copy of the real file, replacing `/dnd-kit|react-virtual/.test(name)` with `/react-virtual/.test(name)` and adding the required `// MEU-49 ... 10-queue-card-ui.md:254-256` comment immediately above it produced 0 `Test-DepGuard` and Packages problems. The existing precedent uses `//` comments at `queue-card.test.ts:809-814` for the assertion beginning at :815-818, so the accepted comment prefixes and 12-line window fit the cited local style. | `named-sets.json:79-90`; `ui/tests/unit/queue-card.test.ts:799-818`; `C:/Temp/av-kit/r7-correct-real.txt`; `C:/Temp/av-kit/r7-review-direct-functions.txt` |
| (e) Both modes | **Correct.** Task row 2 owns AC-49.2 and closes under `DepsPackages`; row 2a depends on row 2 and closes under full `Deps`, so the guard must already be present in either mode. | `task.md:32-33`; `assert-plan-gates.ps1:425-432,1597-1602` |

### Round-7 Regression Checks

| Surface | Result | Evidence |
|---|---|---|
| `New-GoodTree` and prior Deps fixtures | **Pass.** The good tree returned 0 in Full mode. Direct actual-function probes still produced their own expected outcomes with no guard noise: partial migration 2 user-event problems; no setup 1 setup problem; old style 3 retired-mount problems; no RTL 3 mount-predicate problems; mount-only exemption 0; partition gap/overlap 1 each and the real partition 0. | `assert-plan-gates.ps1:889-956,1141-1250,1326-1331`; `C:/Temp/av-kit/r7-review-direct-functions.txt` |
| `PLAN_GATE_SCRIPT.gates.Deps` description | **Pass.** It now describes Packages as manifests/lock/rejections/jest-dom plus `DND_DEP_GUARD_CHECK`, and Full as all of Packages plus the row-2a adoption half, matching the switch and call placement. | `named-sets.json:259-272`; `assert-plan-gates.ps1:314-432,1597-1602` |
| Census supersession and zero-hit behavior | **Pass.** `C10` points to `C13`; the full census reports `[C10 -> C13] "now **69** cases" - gone as expected`, while the ordinary missing-edit query still selects zero-hit `new` rows only when `SupersededBy` is empty. Round-7 `R6-F1`, `C12`, and `C13` new values all have hits; zero-hit NEW values are `(none)`. | `run-correction-census.ps1:303-321,645-654,682-692`; `C:/Temp/av-kit/r7-review-census-full.txt`; `C:/Temp/av-kit/r7-review-census/census-index.txt` |
| Counts and task shape | **Pass.** Parsed current state: 102 top-level named-set keys; exactly 39 unique AC ids, continuous from AC-49.1 through AC-49.39; `task.md` remains 109 lines with the same 29 actionable row ids and no added row. | `C:/Temp/av-kit/r7-artifact-counts.txt` |

### Independently Run Verification

Every command used `rtk proxy`, redirected all streams to `C:/Temp/av-kit/`, captured
`$LASTEXITCODE` immediately after the child process, and only then read the receipt. Expected live
gate failures below are evidence that this remains an unstarted plan, not test failures in the
review apparatus.

| Command / check | Exit | Result |
|---|---:|---|
| `assert-plan-gates.ps1 -SelfTest` | 0 | PASS — 73 cases across 8 gate groups. Receipt: `C:/Temp/av-kit/r7-review-plan-selftest.txt`. |
| `assert-red-phase.ps1 -SelfTest` | 0 | PASS — 17 cases; baseline 439; 27 required-red, 3 preservation, 3 expected-uncollected. Receipt: `C:/Temp/av-kit/r7-review-red-selftest.txt`. |
| `run-correction-census.ps1 -SelfTest` | 0 | PASS — 11 cases. Receipt: `C:/Temp/av-kit/r7-review-census-selftest.txt`. |
| `run-correction-census.ps1 -Gate S6` | 0 | PASS — `S6: 0 finding(s)`. Receipt: `C:/Temp/av-kit/r7-review-census-s6.txt`. |
| `assert-plan-gates.ps1 -Gate DepsPackages` on the live tree | 1 | Expected FAIL — exactly 16 problems: Round 6's 15 plus the broad dependency guard. Receipt: `C:/Temp/av-kit/r7-review-live-depspackages.txt`. |
| `assert-plan-gates.ps1 -Gate Deps` on the live tree | 1 | Expected FAIL — exactly 117 problems: Round 6's 116 plus the same guard failure. Receipt: `C:/Temp/av-kit/r7-review-live-deps.txt`. |
| Full correction census | 0 | PASS for auditability — 101 values, 202 variants, 787 hits; S6 0; zero-hit NEW values none; C10 -> C13 gone as expected. Receipt: `C:/Temp/av-kit/r7-review-census-full.txt`. |
| Direct actual-function attack suite | 0 | The false-pass, boundary, four guard negatives, corrected-real-file positive, good tree, and prior Deps fixtures produced the results recorded above. Receipt: `C:/Temp/av-kit/r7-review-direct-functions.txt`. |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | Pass | AC-49.2, task row 2, `DND_DEP_GUARD_CHECK`, and `DepsPackages` now name and enforce the same row-2 result; no task row was added. |
| PR-2 Not-started confirmation | Pass | All 29 actionable task rows remain unchecked; the live Packages and Full gates fail on the expected preimplementation state. |
| PR-3 Task contract completeness | Pass | Round 7 changed row-2/row-12 validation text, not the task table shape or dependency chain. |
| PR-4 Validation realism | Pass | The exact tree that false-passed in Round 6 now fails for the missing AC-49.2 deliverable; the corrected boundary and corrected real-file copy pass. |
| PR-5 Source-backed planning | Pass | The executable contract is explicitly the local-canon twin of `DND_DEP_GUARD_SUPERSESSION`; no new product behavior or criterion was introduced. |
| PR-6 Correction readiness | Pass | The rolling correction log is present, the full census has no zero-hit ordinary `new` value, and all claimed scripts reproduce. |
| PR-7 Scope discipline | Pass | The correction does not split the MEU or alter OQ-5. The human-decided no-split disposition remains settled. |
| PR-8 Control reachability/totality | Pass | Packages and Full both reach `Test-DepGuard`; the prior missing-deliverable false pass is closed. |
| PR-9 Single-statement discipline | Pass | The rewritten gate description references the one named `DND_DEP_GUARD_CHECK` and matches the executable two-mode contract. |

### Open Questions / Assumptions

None. OQ-5 remains human-decided and was not re-litigated.

### Follow-up Actions

None for plan correction. The plan is safe to implement under the project's normal plan-to-execution
gate; this review does not start implementation.

### Residual Risk

The literal-substring predicate remains intentionally proportionate rather than tamper-proof, as
already bounded by the Round-6 review and the human's Round-7 scope. No execution row authorizes a
builder to rewrite the reviewed named contract or fixture inventory. Ordinary implementation risk
remains in Electron drag coordinates and cross-route external-store wiring, but no unresolved
plan-level blocker remains.

### Verdict

`approved` — R6-F1 is closed: the actual Packages function now rejects the demonstrated missing-guard
tree, accepts the exact row-2 boundary and a correctly edited copy of the real guard, and still leaves
Full mode responsible for row 2a. The Round-7 edits introduced no substantive regression, so the plan
is safe to implement.
