---
date: "2026-08-28"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md"
verdict: "changes_required"
findings_count: 1
round: 7
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
dispatch_id: "p10-queue-card-foundations-plan-r7"
---

# Critical Review: p10-queue-card-foundations

> **Review Mode**: `plan`
> **Verdict**: `changes_required`

---

## Intent Anchor

Executing this plan is supposed to deliver Session 19 only: Phase 10 canon/tokens, additive backend re-queue widening, shared queue primitives, and presentational QueueCard/List/EmptyDropZone components, while wiring nothing to a page and keeping routes, MCP actions, dependencies, and E2E-wave count flat. As written, it cannot reliably deliver that objective because several mandatory controls are nonfunctional, contradictory, or demonstrably false-passing.

## Scope

**Review targets**:

- `docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md`
- `docs/execution/plans/2026-08-28-p10-queue-card-foundations/task.md`
- `docs/execution/plans/2026-08-28-p10-queue-card-foundations/named-sets.json`
- All five supplied `assert-*.ps1` control scripts

**Canonical sources checked**: proposal rev 2 and mockup; Session 19 grouping; the queue/state/shared-component sections of `06-gui.md`; `gui-actions-index.md`; `build-priority-matrix.md`; emerging standards G20 and G30-G37; current domain enums/transitions/guards, repository bulk reset, and the cited existing tests.

**Review Type**: first-pass plan review. **Checklist Applied**: PR-1 through PR-9, DR-1 through DR-8, Boundary Input Contract, C2, Sweep 8, single-statement discipline, and PR-8 control binding.

**Out of scope**: product/test/plan edits; project tests or generators; Capture; page migration; reopening the USER_EXPLICIT `human` execution gate.

---

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | High | **PR-4 / PR-8 — the Red oracle never constructs `$names`, so every Red row is nonfunctional and the advertised text fallback does not exist.** After creating `$ids`, the script jumps directly to `$names \| Where-Object`; `JsonReceipt` is never read and no receipt lines are parsed. The p9 analog's omitted block is exactly the block that populated UI JSON or text names. Consequently valid UI JSON, pytest snake-case names, and the claimed no-plugin text path all fail before the multi-ID rejection can prove anything. Prefixes and counts themselves are correct: no trailing dots, and 8/9/13/13 match the AC tables; the multi-ID mapping logic is sound but unreachable. | `assert-red-oracle.ps1:72-87`; `implementation-plan.md:511-513`; `task.md:45`, `task.md:48`, `task.md:51`, `task.md:54` | Restore explicit UI-JSON and text-receipt name extraction before `Get-IdPattern`; add static/self-test fixtures proving dotted UI ids, snake-case pytest ids, optional-json text fallback, unrelated failures, and a stuffed multi-ID title. | open |
| 2 | High | **PR-8 — `PAGE_ISOLATION_CHECK` can pass a materially migrated queue.** It scans feature TSX text only for five import substrings, then checks a scalar E2E count and whether preserved ids remain anywhere in the registry. `ConvertQueueTable.tsx` or `DownloadQueueTable.tsx` can replace table markup inline while retaining registry ids/counts and importing none of those strings; a barrel/re-export import also bypasses the list. Thus the declared MEU-42 carve-out is not constrained to the two import/helper-deletion edits, and a real migration can satisfy the sole executable owner of “nothing wired.” | `assert-page-isolation.ps1:10-27`, `assert-page-isolation.ps1:29-54`; `implementation-plan.md:535-545`; `named-sets.json:447-448` | Bind the negative oracle to actual page/file deltas: require zero changes to page entrypoints, and structurally constrain the two queue-table diffs to the shared `formatFileSize` import plus deletion of the local definition. Also reject direct and re-exported reachability to the new component surface and preserve E2E test identities, not only their count. | open |
| 3 | High | **Boundary Input Contract / PR-9 — the envelope extra-field behavior has two materially different live contracts.** The Boundary Inventory requires Zod `.strict()` and rejection of unknown wrapper keys, while AC-42.11 says the same parser “ignores unknown wrapper keys.” No named policy or precedence rule says which governs, so implementation and negative tests cannot satisfy a single external-input contract. | `implementation-plan.md:327`; `implementation-plan.md:348` | Choose one source-backed policy. Under the repository Boundary Input Contract, make `.strict()`/unknown-key rejection canonical and add the unknown-key adversary to AC-42.11 and its error-surface assertion. | open |
| 4 | High | **PR-8 — the WCAG contrast oracle is not bound to the rendered foreground/fill/background values.** AC-42.2 supplies one `hexDark`/`hexLight` pair tied by AC-42.4 to the status `token`, but actual pill classes can use different tokens: proposal Pending is `bg-neutral/20 text-fg-muted`, and Cancelled is `bg-bg-elevated text-fg-muted`. The plan names no theme-background input or class-to-token resolver, while calling AC-42.3 a pure function over `status-tokens.ts`. A test can therefore compute ≥4.5 from the status token pair while the rendered `textClass`/`fillClass` combination has different colors. | `implementation-plan.md:339-341`; `implementation-plan.md:360`; `named-sets.json:153-163`; `docs/proposals/2026-08-27-queue-card-ui-proposal.md:96-110` | Define one canonical per-status foreground token, fill token, alpha, and theme background source. Make the test resolve those exact classes against both theme blocks in `styles.css`, alpha-composite the fill, and mutate foreground/fill/background bindings in negative fixtures. | open |
| 5 | High | **P0 / PR-4 — all four numbered Red validations leave the oracle process unredirected.** Each row redirects the test process and captures its code, then invokes `assert-red-oracle.ps1` as a second top-level process without `*> C:/Temp/av-kit/...`. That violates the non-negotiable every-process redirect rule even after Finding 1 is fixed. The Markdown `\|` escapes are otherwise structurally correct: every actionable table row still parses to the expected 12 cells. | `task.md:45`; `task.md:48`; `task.md:51`; `task.md:54` | Wrap each complete Red sequence in one redirected outer `pwsh`, or give the oracle its own all-stream receipt; capture its `$LASTEXITCODE` immediately before any receipt read and propagate it. | open |
| 6 | Low | **Named-set consumption census: 26 top-level keys are orphans.** No exact consumer exists outside `named-sets.json` for `_meta`, `PLAN_DIR`, `PROJECT_SLUG`, `PHASE`, `MEU_ROW_KEYS`, `PROPOSAL`, `MOCKUP`, `RECEIPT_DIR`, `HANDOFF_DIR`, `RED_KIND_40..43`, `RED_TOTAL`, `DOWNLOAD_STATUSES`, `CONVERSION_STATUSES`, `OPENAPI_EXPORT`, `MCP_CHANGE_REQUIRED`, `STANDARDS_IN_SCOPE`, `G35_RULE`, `SESSION19_STATUS_AT_PLAN`, `EXEC_REVIEW_TARGET`, `PLAN_REVIEW_TARGET`, `PLAN_REVIEW_MODE`, `UI_ESLINT`, or `VITEST_ALLOW_ONLY`. The four `RED_PREFIX_*` keys were excluded from this list because the Red script consumes them dynamically. No dangling direct `$sets.<key>` reference was found. | `named-sets.json:2-41`; `named-sets.json:74-84`; `named-sets.json:115-132`; `named-sets.json:307-340`; `named-sets.json:407-444` | Delete unused keys or bind each to an executable/plan/task consumer; keep metadata outside the executable set if it is not contract input. | open |
| 7 | Low | **PR-7 C2 labeling drift.** Repointing `--color-status-pending` and the new Playwright wave are marked `out-of-scope` while naming MEU-44/45 and MEU-44 deferrals; the Session 20/21 `/create-plan` row uses `MEU-44+` instead of a concrete registered MEU. The grouping provides real bases, so this is clerical rather than disguised missing work. | `implementation-plan.md:468`; `implementation-plan.md:471-472` | Relabel the first two rows `deferred`; split or name the concrete MEU owner for the `/create-plan` row. | open |

No Critical findings were identified.

---

## Commands Executed

All shell work was static and redirected under `C:/Temp/av-kit/`; `$LASTEXITCODE` was captured before receipt reads. No pytest, Vitest, npm test/build, Playwright, MEU status command, OpenAPI generator, assert script, or product test/generator was run.

Key receipts:

- Protocol/session authorities: `plan-review-protocols.txt`, `plan-review-workflow-1.txt`, `plan-review-workflow-2.txt`, `plan-review-session-authorities.txt`
- Line-numbered target reads: `plan-review-plan-1.txt` through `plan-review-plan-3.txt`, `plan-review-task.txt`, `plan-review-sets-1.txt` through `plan-review-sets-3.txt`, `plan-review-assert-scripts.txt`
- Red counts/prefix audit: `plan-review-red-counts.json`; p9 analog comparison: `plan-review-analog-red.txt`
- Page/control and task-shape audit: `plan-review-task-shape.json`, `plan-review-unstarted-state.json`
- Named-set consumption: `plan-review-named-set-orphans.json`, `plan-review-dangling-candidates.json`
- Sweep 8/reference existence: `plan-review-reference-existence.json`
- MEU-41 static evidence: `plan-review-requeue-tests.txt`, `plan-review-requeue-static-details.txt`, `plan-review-requeue-repository.txt`
- Proposal/grouping/build/standards evidence: `plan-review-proposal.txt`, `plan-review-mockup-census.txt`, `plan-review-grouping.txt`, `plan-review-build-authorities.txt`, `plan-review-emerging-details.txt`
- Canonical pre-edit guard: `plan-review-pre-edit-guard.json`

---

## Checklist Results

### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | Both artifacts cover MEU-40→43 in the same order, with no page migration, no new dependency/E2E wave, and the same H1/review/H2 sequence. |
| PR-2 Not-started confirmation | pass | All actionable task rows are unchecked; all four MEU handoffs, implementation review, reflection, and Phase 10 spec are absent. The Phase 10 spec is explicitly scheduled by MEU-40. |
| PR-3 Task contract completeness | pass | Every actionable row has Task, Owner, Deliverable, Validation, dependency, context strategy, durable output, builder model, and Status cells. All table rows retain 12 cells despite escaped pipes. |
| PR-4 Validation realism | **fail** | Findings 1, 2, 4, and 5 demonstrate nonfunctional, false-passing, or P0-invalid gates. |
| PR-5 Source-backed planning | pass | AC sources use Spec, Local Canon, Research-backed, or Human-approved bases; no unsourced product behavior was found. |
| PR-6 Handoff/corrections readiness | pass | Four MEU handoff paths and one rolling execution-review path are explicit. This is Round 1; corrections route through `/plan-corrections`. |
| PR-7 Scope discipline | pass with Low correction | MEU-44–48 deferrals exist in the grouping and Capture is source-backed out of scope. Finding 7 is labeling drift only. |
| PR-8 Control reachability and totality | **fail** | Findings 1, 2, and 4 show an unreachable oracle and concrete false-pass paths. MEU-41's service/domain call chain and repository-bulk separation are otherwise correctly distinguished. |
| PR-9 Single-statement discipline | **fail** | Finding 3 is a materially conflicting boundary policy; Finding 6 records orphan executable keys. Other repeated sets/counts are consistently named. |

### Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | fail in plan-control sense | The Red fallback, page-isolation, and contrast claims overstate what their declared controls can prove. |
| DR-2 Residual old terms | pass | Existing `reset_failed`, DataTable/glyph sections, and old queue tables are intentionally preserved or superseded by pointer; no accidental rename/delete is planned. |
| DR-3 Downstream references updated | pass in scope | Phase 10 SSOT/matrix/hub registration, `06-gui.md` pointers, OpenAPI regen, testid registry, and handoffs are inventoried. |
| DR-4 Verification robustness | **fail** | Findings 1, 2, 4, and 5 materially weaken required gates. |
| DR-5 Evidence auditability | fail | Most commands are reproducible, but the Red oracle and four Red receipt forms are not valid evidence paths. |
| DR-6 Cross-reference integrity | fail | Finding 3 gives incompatible unknown-field semantics for the same envelope parser. |
| DR-7 Evidence freshness | pass | Static counts reproduce: ACs 8/9/13/13; OpenAPI operations 71; current MCP tests/registry canon assert 67 actions. Existing negative reset assertions use Pending or Done. |
| DR-8 Completion vs residual risk | pass | The plan remains draft/unstarted and does not claim implementation completion. |

### Focused Contract Results

| Contract | Result | Evidence |
|----------|--------|----------|
| Red prefixes/counts | pass | `AC-40`/`41`/`42`/`43`, no trailing dot; 8/9/13/13 match the actual AC rows. |
| Stuffed multi-ID rejection | fail operationally | Mapping logic would reject multiple mapped ids, but `$names` is never populated, so the control is unreachable. |
| MEU-41 additive-only claim | pass | Existing cited negative assertions seed Pending or Done; repository `reset_failed()` is the distinct bulk protocol/infra method; `CONVERSION_TRANSITIONS` currently covers every `ConversionStatus`. |
| Contrast machine-checkability | fail | Finding 4: one status-token hex pair cannot bind differing foreground/fill/background classes. |
| Python text fallback | fail | Finding 1: no text-line parser exists in the p10 script. |
| Task P0 receipts | fail | Finding 5 affects numbered Red rows 2, 5, 8, and 11; other actionable rows have an outer redirect/capture/propagation path. |
| Named-set references | fail with Low cleanup | All direct script/task references resolve; 26 top-level keys are unconsumed (Finding 6). |
| Referenced-artifact existence | pass | All invoked existing scripts/tools/templates are present. `docs/build-plan/10-queue-card-ui.md` and new implementation files are absent but explicitly scheduled deliverables. |

---

## Open Questions / Assumptions

- The direct user instruction locking `PLAN_TO_EXEC_GATE="human"` governs this dispatch despite `.agent/context/harness.local.md`; an approved future verdict would still require the user's next explicit message before execution.
- The Session 19 grouping's zero-new-wave/no-page-migration decision is accepted as the governing scope and was not relitigated.
- No external research was needed: the supplied proposal, mockup, grouping, local canon, and current repository state were sufficient.

## Follow-up Actions

Route one correction pass through `/plan-corrections`:

1. Restore and self-test Red receipt parsing, then make all four Red commands P0-compliant.
2. Replace the page-isolation substring/count gate with a delta- and reachability-bound negative oracle that enforces the two-file import-only carve-out.
3. Resolve envelope unknown-field behavior to one strict contract.
4. Bind contrast calculation to the actual rendered foreground, fill/alpha, and both theme backgrounds.
5. Remove/bind named-set orphans and correct the C2 Kind/MEU labels.

## Residual Risk

After correction, implementation-time Electron/Playwright execution may still be sandbox-blocked under the registered `E2E_SANDBOX` path, and real card behavior remains intentionally unreachable until MEU-44 mounts it. Those are accepted execution risks; they do not excuse the current false-passing/static-control defects.

---

## Verdict

`changes_required` — five evidence-backed High findings show that the current plan cannot execute its mandatory Red proof, can accept a page migration while claiming nothing is wired, gives incompatible external-input semantics, can report contrast without binding the rendered colors, and violates P0 in every numbered Red validation. The MEU-41 additive widening, AC counts, scheduled Phase 10 canon absence, Capture exclusion, flat route/MCP scope, and human execution gate are otherwise correctly represented.

---

## Round 2 — Corrections Re-Review

### Intent Anchor

Executing this plan is supposed to deliver Session 19 only: Phase 10 canon and tokens, additive backend re-queue widening, shared queue primitives, and presentational QueueCard/List/EmptyDropZone components, while wiring nothing to a page and keeping routes, MCP actions, dependencies, and the E2E-wave count flat. Round 2 cannot determine whether the corrected plan would deliver that objective because the resubmission is missing the mandatory correction blast-radius evidence required before substantive re-review.

### Pre-Verdict Procedural Gate

`changes_required` under PR-6's procedural exception. The resubmission does not name an untruncated blast-radius census receipt for the Round 1 corrections, and the rolling review file contains no correction log assigning every census `file:line` hit an `updated` or `confirmed-consistent` disposition. The full plan-folder/review search found only Round 1 review prose, task receipt references, and Round 2 dispatch claims; it found no correction census receipt or disposition record (`C:/Temp/av-kit/r2-correction-gate-search.txt`).

This is not a severity-rated finding. `.agent/workflows/plan-critical-review.md:256` and `:287-288` require a Round 2 `changes_required` verdict naming this precondition alone and prohibit review of corrected content when the census is missing, truncated, or undispositioned. `.agent/workflows/plan-corrections.md:170-220` separately requires old/new fixed-string sweeps, untruncated receipts, semantic-variant declarations, and a per-hit correction log.

### Round 1 Finding Resolution

The statuses below mean procedurally unresolved, not that the corrected artifacts were found defective. Content adjudication was not permitted after the PR-6 gate failed.

| Finding | Round 2 status | Evidence |
|---------|----------------|----------|
| F1 — Red oracle never constructs `$names` | `unresolved` | Not adjudicated; mandatory correction census and disposition log absent. |
| F2 — page-isolation can pass a migrated queue | `unresolved` | Not adjudicated; mandatory correction census and disposition log absent. |
| F3 — conflicting envelope extra-field contract | `unresolved` | Not adjudicated; mandatory correction census and disposition log absent. |
| F4 — WCAG oracle not bound to rendered values | `unresolved` | Not adjudicated; mandatory correction census and disposition log absent. |
| F5 — unredirected Red oracle invocations | `unresolved` | Not adjudicated; mandatory correction census and disposition log absent. |
| F6 — orphan named-set keys | `unresolved` | Not adjudicated; mandatory correction census and disposition log absent. |
| F7 — C2 labeling drift | `unresolved` | Not adjudicated; mandatory correction census and disposition log absent. |

### New Findings

No new severity-ranked findings were assessed. PR-6 is a pre-verdict procedural gate rather than a finding, so Round 2 `findings_count` is `0`.

### Checklist Results

#### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | not assessed | Substantive review stopped at PR-6. |
| PR-2 Not-started confirmation | not assessed | Substantive review stopped at PR-6. |
| PR-3 Task contract completeness | not assessed | Substantive review stopped at PR-6. |
| PR-4 Validation realism | not assessed | The corrected Red, isolation, contrast, and receipt controls were not adjudicated. |
| PR-5 Source-backed planning | not assessed | The rewritten F3/F4 AC source bindings were not adjudicated. |
| PR-6 Handoff/corrections readiness | **fail — pre-verdict gate** | No named untruncated correction census receipt and no per-hit disposition log exist in the supplied resubmission evidence. |
| PR-7 Scope discipline | not assessed | The corrected C2 table was not adjudicated. |
| PR-8 Control reachability and totality | not assessed | The corrected controls and negative oracles were not adjudicated. |
| PR-9 Single-statement discipline | not assessed | The corrected named-set binding model and repeated literals were not adjudicated. |

#### Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | not assessed | Correction claims were not accepted without the required census/log evidence. |
| DR-2 Residual old terms | not assessed | Substantive review stopped at PR-6. |
| DR-3 Downstream references updated | not assessed | Substantive review stopped at PR-6. |
| DR-4 Verification robustness | not assessed | Oracle self-tests and adversarial probes were not run after the pre-verdict gate failed. |
| DR-5 Evidence auditability | **fail** | The correction resubmission omits the required raw census receipt and interpreted per-hit log. |
| DR-6 Cross-reference integrity | not assessed | Substantive review stopped at PR-6. |
| DR-7 Evidence freshness | **fail** | Round 2 correction claims are not backed by the mandatory reproducible correction census evidence. |
| DR-8 Completion vs residual risk | pass | The plan remains unstarted and no implementation-complete claim was made. |

### Commands and Evidence

All shell work was static and redirected under `C:/Temp/av-kit/`; `$LASTEXITCODE` was captured before receipt reads. No project test, generator, MEU command, OpenAPI command, Playwright command, page-isolation `-Capture`, or plan-local oracle self-test was run.

- Protocol and governance reads: `r2-terminal-preflight.txt`, `r2-output-policy.txt`, `r2-review-workflow-full.txt`, `r2-review-workflow-tail.txt`, `r2-plan-corrections-step5c.txt`, and the session profile/context receipts.
- Existing rolling review and plan-folder inventory: `r2-review-file-existing.txt`, `r2-plan-folder-list.txt`.
- PR-6 search: `r2-correction-gate-search.txt`; governing line receipt: `r2-pr6-rule-lines.txt`.
- Template and recent peer exemplar: `r2-review-template-full.txt`, `r2-peer-review.txt`.
- Canonical pre-edit guard: `r2-pre-edit-guard.txt` (`exact_match=true`).
- Post-write structure/frontmatter/variant check: `r2-review-structural-check.txt`; completion-preflight task-state census: `r2-task-status-count.txt` (27 actionable rows, all still open as required for an unstarted plan).

The two permitted self-tests were intentionally not run: PR-6 requires stopping corrected-content review at the failed pre-verdict gate, and executing those scripts would have substantively adjudicated the corrected controls.

### Follow-up Action

Before Round 3, the corrections agent must append a correction log to this rolling file and identify the untruncated census receipt(s). For every changed literal, term, count, set, threshold, or predicate—and each declared semantic variant—the log must disposition every receipt hit as `updated` or `confirmed-consistent`. The next reviewer can then verify the receipt/log pair and, if PR-6 passes, re-audit all seven Round 1 fixes and the full requested control surface.

### Residual Risk

All seven claimed fixes remain substantively unaudited this round. In particular, no conclusion was reached on self-test honesty, capture ordering or re-capture laundering, queue-migration bypasses, status-pill token consistency, envelope strictness, P0 Red commands, or whether transitive named-set documentation launders an executable-contract gap. Round 3 is the final configured plan-review round.

### Verdict

`changes_required` — the Round 2 resubmission fails the mandatory PR-6 evidence precondition. This verdict names no severity-rated finding and does not reject any claimed fix on its merits; it requires the missing correction census and per-hit disposition log before the final substantive review round. Execution remains blocked behind the user's explicit `human` gate regardless of any later `approved` review verdict.

---

## Round 2 Corrections — Blast-Radius Census (corrections agent)

> Appended by the corrections agent in response to the Round 2 PR-6 pre-verdict gate, which
> required a named untruncated census receipt and a per-hit disposition log before Round 3 may
> adjudicate the seven Round 1 fixes on their merits. This section supplies both. It records no
> verdict — that remains the reviewer's.

**Blast-radius census (Round 2 scope — `old`/`new` only): 17 values changed, 59 literals swept, 102
sites found, 55 updated, 47 confirmed consistent. SUPERSEDED by the Round 3 variant sweep below;
the complete figures are 82 literals / 216 sites.**

### Reproduction

The census is a script plus a declared input table, not a transcript, so the reviewer can re-run
it rather than trust it:

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-28-p10-queue-card-foundations/run-correction-census.ps1 *> C:/Temp/av-kit/census-run.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/census-run.txt; exit $code
```

- Input table (one entry per changed value, with its declared semantic variants):
  `docs/execution/plans/2026-08-28-p10-queue-card-foundations/correction-census.json`
- Driver: `docs/execution/plans/2026-08-28-p10-queue-card-foundations/run-correction-census.ps1`
- Receipts, **untruncated, one file per swept literal**: `C:/Temp/av-kit/census/census-{slug}-{old|new}-{i}.txt`
- Receipt index (slug, direction, literal, rg exit code, hit count): `C:/Temp/av-kit/census/INDEX.txt`
- Predicate census: `C:/Temp/av-kit/census/census-red-counts-predicate.txt`
- Run receipt: `C:/Temp/av-kit/census-run.txt`

Every sweep is `rg -F -n` (literal text, so a regex metacharacter inside a value cannot silently
change what was searched) across **both** plan files, in **both** directions. Nothing is `head`ed,
`Select-Object`ed, or piped. `rg` exit codes are captured per literal and recorded in the index:
`0` = matched, `1` = no match, `>1` = execution error (the driver fails the run on `>1`; none
occurred). A `1` on an *old* literal is the good outcome; a `1` on a *new* literal is reported in
the log as a finding about the sweep rather than passed over — two such cases appear below, both
because the corrections agent declared a variant key name that does not exist.

### Semantic variants declared before sweeping

A fixed-string sweep cannot find a rephrasing. Each entry in `correction-census.json` carries a
`variants` field naming every other form the value plausibly takes in this plan — the prose form,
the set-literal form, the class-name form, the printed-receipt form.

> **RETRACTED — this paragraph originally read "Those variants were swept as additional literals;
> they are the `new/1..3` rows in the log below." That claim was false**, and Round 3 proved it:
> `run-correction-census.ps1` iterated only `old` and `new`, so not one of the declared variants was
> ever swept, and the `new/1..3` rows named above are later elements of each entry's `new` array.
> The driver still printed `PASS`. Corrected in `## Round 3 Corrections` below, which supplies the
> variant sweep, its receipts, and its dispositions. This retraction is left in place rather than
> edited away, because the claim-to-state failure is itself the finding.

### Predicate census — AC counts after the F3/F4 AC rewrites

The F3 and F4 corrections rewrote AC text inside MEU-42 (and F6 rewrote AC-41.1). `RED_COUNT_4x`
is the declared per-MEU AC count that the Red oracle enforces, so a rewrite that added or dropped
an AC row would silently desynchronise it. Counted structurally from the AC tables rather than by
fixed string:

| meu | declared RED_COUNT | AC rows found in plan | verdict |
|-----|--------------------|-----------------------|---------|
| 40 | 8 | 8 | MATCH |
| 41 | 9 | 9 | MATCH |
| 42 | 13 | 13 | MATCH |
| 43 | 13 | 13 | MATCH |

### One regression the census caught

`carve-out-doorway / old` was expected to return no hits and returned one:
`implementation-plan.md:555` still asserted the **superseded** substring rule — "no file ... may
contain any `NEW_SURFACE_MODULES` string" — one clause before the sentence that says the oracle
resolves import specifiers instead. The F2 rewrite had replaced the mechanism and appended the
explanation without deleting the original claim, leaving the section self-contradictory at exactly
the point R1-F2 was about. Corrected to "may **resolve** an import specifier to any
`NEW_SURFACE_MODULES` entry"; the sweep now returns `rc=1`. This is the regression class Step 5c
exists to catch, and it was found by the census rather than by the reviewer.

### Per-hit disposition log

Every hit in every receipt carries exactly one disposition. `updated` = the site was edited this
round; `confirmed-consistent` = the site already stated the value and still agrees. Zero-hit
literals are listed too, with what the absence proves.

| Value | Dir | Literal swept | rc | Sites | Disposition | Reason |
|-------|-----|---------------|----|-------|-------------|--------|
| `red-oracle-key` | old | `RED_ORACLE_CHECK` | 1 | none | n/a | no stale `RED_ORACLE_CHECK` remains in either plan file (the one surviving mention, a comment header in assert-red-oracle.ps1, was also corrected) |
| `red-oracle-key` | new | `RED_ORACLE` | 0 | `task.md:45` `task.md:48` `implementation-plan.md:76` `implementation-plan.md:79` `implementation-plan.md:82` `implementation-plan.md:85` | **updated** | the four Red rows and four WP rows now cite `RED_ORACLE`; the duplicate key is deleted |
| `red-selftest` | old | `both must pass before row 2` | 1 | none | n/a | the two-precondition wording is gone |
| `red-selftest` | new | `RED_SELFTEST` | 0 | `task.md:44` `implementation-plan.md:516` | **updated** | row 1 preamble + Verification Plan now name the Red self-test as a precondition |
| `red-selftest` | new | `All three must pass before row 2` | 0 | `task.md:44` | **updated** | row 1 gate wording changed from two preconditions to three |
| `red-selftest` | new | `red-oracle-selftest.txt` | 0 | `task.md:44` | **updated** | row 1 durable outputs gained the self-test receipt |
| `page-iso-selftest` | old | `and run 'RED_SELFTEST'; both must pass` | 1 | none | n/a | the pre-fix row 1 preamble is gone |
| `page-iso-selftest` | new | `PAGE_ISOLATION_SELFTEST` | 0 | `task.md:44` `implementation-plan.md:569` | **updated** | row 1 + plan section 6 name the isolation self-test |
| `page-iso-selftest` | new | `-SelfTest` | 0 | `task.md:44` | **updated** | row 1 validation chain runs `-SelfTest` before `-Capture` |
| `page-iso-selftest` | new | `SELFTEST_DIR` | 0 | `implementation-plan.md:569` | **updated** | plan section 6 names the hermetic fixture root |
| `page-iso-selftest` | new | `page-iso-selftest.txt` | 0 | `task.md:44` | **updated** | row 1 durable outputs gained the self-test receipt |
| `row1-deliverable` | old | `hub bound; 'PAGE_BASELINE' captured` | 1 | none | n/a | the pre-fix deliverable wording is gone |
| `row1-deliverable` | new | `both oracle self-tests green` | 0 | `task.md:44` | **updated** | row 1 deliverable now asserts both self-tests green before the baseline |
| `e2e-count` | old | `61` | 1 | none | n/a | the wrong count 61 appears nowhere |
| `e2e-count` | new | `55` | 0 | `implementation-plan.md:270` `implementation-plan.md:287` | **confirmed-consistent** | BOTH hits are unrelated substring matches (`extra="forbid"` row and an AC-41.8 route body), NOT statements of the E2E count. The count is stated exactly once, as `E2E_BASELINE_COUNT` = 55 in named-sets.json, and is never inlined in either plan file -- which is the single-statement rule holding, not a miss |
| `e2e-count` | new | `E2E_COUNT` | 1 | none | n/a | declared variant `E2E_COUNT` does not exist -- the real key is `E2E_BASELINE_COUNT`. Recorded rather than quietly re-swept; the count itself is dispositioned above |
| `e2e-count` | new | `E2E_BASELINE_BASIS` | 0 | `implementation-plan.md:565` | **updated** | plan section 6 now cites the basis (49 in *.test.ts + 6 in *.spec.ts) instead of restating a bare number |
| `e2e-count` | new | `E2E_TITLE_SET` | 1 | none | n/a | declared variant `E2E_TITLE_SET` does not exist as a named key -- the title set lives inside `PAGE_BASELINE` and is described in plan section 6 prose |
| `envelope-policy` | old | `ignores unknown wrapper keys` | 1 | none | n/a | the "ignores unknown wrapper keys" contract is gone |
| `envelope-policy` | old | `ignore unknown wrapper keys` | 1 | none | n/a | no singular-verb variant survives either |
| `envelope-policy` | new | `ENVELOPE_UNKNOWN_KEY_POLICY` | 0 | `implementation-plan.md:348` | **updated** | AC-42.11 rewritten to assert rejection under the single named policy |
| `envelope-policy` | new | `.strict()` | 0 | `implementation-plan.md:327` `implementation-plan.md:348` | **confirmed-consistent** | Boundary Inventory (327) already required `.strict()`; AC-42.11 (348) now agrees with it instead of contradicting it |
| `contrast-binding` | old | `hexDark` | 1 | none | n/a | the single hex pair is gone |
| `contrast-binding` | old | `hexLight` | 1 | none | n/a | the single hex pair is gone |
| `contrast-binding` | new | `STATUS_PILL_TABLE` | 0 | `task.md:46` `task.md:51` `implementation-plan.md:187` `implementation-plan.md:230` `implementation-plan.md:339` `implementation-plan.md:340` `implementation-plan.md:341` `implementation-plan.md:359` `implementation-plan.md:360` `implementation-plan.md:374` | **updated** | the pill table is now the single source for foreground/fill/alpha and is cited by the two Red rows, the testid inventory, AC-40.5, AC-42.2/42.3/42.4, the source table, and the token rationale |
| `contrast-binding` | new | `CONTRAST_BACKDROPS` | 0 | `implementation-plan.md:340` `implementation-plan.md:361` `task.md:51` | **updated** | the backdrop set is cited by AC-42.3, the both-themes source row, and the MEU-42 Red row |
| `contrast-binding` | new | `--color-pill-` | 0 | `implementation-plan.md:360` | **updated** | the ten new foreground tokens are introduced in the source-label row; they are enumerated once in `NEW_TOKENS` and authored by AC-40.3 |
| `contrast-threshold` | old | `4.5:1` | 0 | `implementation-plan.md:150` `implementation-plan.md:360` `implementation-plan.md:361` | **confirmed-consistent** | all three are quotations of source material (the WCAG SC title at 150, the failure rationale at 360, and the proposal quote at 361), not independent contract statements. The contract site is `CONTRAST_MIN` |
| `contrast-threshold` | new | `4.60` | 0 | `implementation-plan.md:360` | **updated** | the worst surviving pairing after the ten new tokens is recorded alongside the rationale |
| `contrast-threshold` | new | `CONTRAST_MIN` | 0 | `implementation-plan.md:243` `implementation-plan.md:340` `implementation-plan.md:360` | **confirmed-consistent** | `CONTRAST_MIN` is the executable statement of the threshold and is unchanged by this round |
| `red-redirect` | old | `assert-red-oracle.ps1 -Kind` | 0 | `task.md:45` `task.md:48` `task.md:51` `task.md:54` `implementation-plan.md:504` `implementation-plan.md:510` | **updated** | the invocation literal is unchanged by design -- what changed is that all six sites now sit inside a redirected sequence with `$LASTEXITCODE` captured immediately. Verified independently: 0 unredirected oracle invocations across 27 actionable rows |
| `red-redirect` | new | `red-oracle-meu-40.txt` | 0 | `task.md:45` `implementation-plan.md:504` | **updated** | MEU-40 oracle receipt introduced |
| `red-redirect` | new | `red-oracle-meu-41.txt` | 0 | `task.md:48` `implementation-plan.md:510` | **updated** | MEU-41 oracle receipt introduced |
| `red-redirect` | new | `red-oracle-meu-42.txt` | 0 | `task.md:51` | **updated** | MEU-42 oracle receipt introduced |
| `red-redirect` | new | `red-oracle-meu-43.txt` | 0 | `task.md:54` | **updated** | MEU-43 oracle receipt introduced |
| `scope-labels` | old | `MEU-44+` | 0 | `task.md:40` | **confirmed-consistent** | the sole surviving `MEU-44+` is task.md:40 "Do not start MEU-44+" -- a forward-scope prohibition, a different statement from the C2 owner label R1-F7 flagged. Left deliberately |
| `scope-labels` | new | `deferred` | 0 | `implementation-plan.md:231` `implementation-plan.md:367` `implementation-plan.md:456` `implementation-plan.md:457` `implementation-plan.md:458` `implementation-plan.md:459` `implementation-plan.md:460` `implementation-plan.md:469` `implementation-plan.md:470` `implementation-plan.md:471` `implementation-plan.md:473` `implementation-plan.md:474` | **confirmed-consistent** | twelve `deferred` labels, of which the two relabeled rows (469, 470) are this round's edit and the rest predate it |
| `scope-labels` | new | `MEU-44` | 0 | `task.md:40` `implementation-plan.md:30` `implementation-plan.md:109` `implementation-plan.md:172` `implementation-plan.md:367` `implementation-plan.md:413` `implementation-plan.md:456` `implementation-plan.md:469` `implementation-plan.md:470` `implementation-plan.md:473` `implementation-plan.md:474` | **confirmed-consistent** | every `MEU-44` reference now names a concrete owner; task.md:40 is the scope guardrail, not a C2 label |
| `scope-labels` | new | `MEU-45` | 0 | `implementation-plan.md:30` `implementation-plan.md:457` `implementation-plan.md:469` | **confirmed-consistent** | `MEU-45` appears only as a concrete deferral owner |
| `frozen-rationale` | old | `byte-frozen for the whole session, proving` | 1 | none | n/a | the duplicated rationale prose is gone; the key is now the single statement |
| `frozen-rationale` | new | `FROZEN_RATIONALE` | 0 | `implementation-plan.md:562` | **updated** | plan section 6 now cites the key instead of restating its text |
| `frozen-rationale` | new | `byte-freezes` | 0 | `implementation-plan.md:563` | **updated** | the surviving prose is the short cited form |
| `openapi-export` | old | `MEU-41 regenerates ('-o') because` | 0 | `implementation-plan.md:533` | **confirmed-consistent** | same line: the sentence was prefixed, not replaced, so the MEU-41 regeneration rule still reads correctly |
| `openapi-export` | new | `OPENAPI_EXPORT` | 0 | `implementation-plan.md:533` | **updated** | the generator is named rather than path-inlined in prose |
| `handoff-dir` | old | `MEU handoffs (first created` | 1 | none | n/a | the un-keyed H1-6 phrasing is gone |
| `handoff-dir` | new | `HANDOFF_DIR` | 0 | `task.md:65` | **updated** | H1-6 now names the directory key |
| `requeue-exhaustiveness` | old | `Chain: import the constants. Negative: the set is inlined in the guard, or duplicated` | 1 | none | n/a | the pre-fix AC-41.1 clause is gone |
| `requeue-exhaustiveness` | new | `REQUEUE_STATUS_EXHAUSTIVENESS` | 0 | `implementation-plan.md:280` | **updated** | AC-41.1 gained the partition-exhaustiveness assertion and its negative oracle |
| `ssot-receipts` | old | `prove 'SSOT_READY'` | 0 | `task.md:62` | **confirmed-consistent** | same line: the citation was always correct, only its definition was missing |
| `ssot-receipts` | new | `SSOT_READY` | 0 | `task.md:62` | **updated** | H1-3 citation now resolves to a defined assertion receipt |
| `ssot-receipts` | new | `SSOT_APPROVED` | 0 | `task.md:71` | **updated** | H2-2 citation now resolves to a defined assertion receipt |
| `carve-out-doorway` | old | `may contain any 'NEW_SURFACE_MODULES' string` | 1 | none | n/a | CORRECTED THIS ROUND. The census found plan section 6 still asserting the superseded substring rule ("may contain any `NEW_SURFACE_MODULES` string") one clause before the sentence saying the opposite. Rewritten to "may **resolve** an import specifier to any `NEW_SURFACE_MODULES` entry". This is exactly the regression class Step 5c exists to catch |
| `carve-out-doorway` | new | `CARVE_OUT_ALLOWED_IMPORT` | 0 | `implementation-plan.md:552` `implementation-plan.md:562` | **updated** | the allowed import is named in the carve-out rule and in the doorway narrowing |
| `carve-out-doorway` | new | `resolved suffix` | 0 | `implementation-plan.md:560` | **updated** | plan section 6 states that matching is against the resolved suffix, not the exempt directory |
| `red-counts` | old | `8/9/13/13` | 1 | none | n/a | the counts are never written as a joined literal; they are stated once each as `RED_COUNT_4x` and checked structurally by the predicate census |
| `red-counts` | new | `RED_COUNT_40` | 0 | `task.md:45` `implementation-plan.md:76` | **confirmed-consistent** | MEU-40 AC count unchanged at 8; predicate census MATCH |
| `red-counts` | new | `RED_COUNT_41` | 0 | `task.md:48` `implementation-plan.md:79` | **confirmed-consistent** | MEU-41 AC count unchanged at 9 despite the AC-41.1 rewrite; predicate census MATCH |
| `red-counts` | new | `RED_COUNT_42` | 0 | `task.md:51` `implementation-plan.md:82` | **confirmed-consistent** | MEU-42 AC count unchanged at 13 despite the F3 and F4 AC rewrites; predicate census MATCH |
| `red-counts` | new | `RED_COUNT_43` | 0 | `task.md:54` `implementation-plan.md:85` | **confirmed-consistent** | MEU-43 AC count unchanged at 13; predicate census MATCH |

## Round 3 — Final Configured Round

### Intent Anchor

Executing this plan is supposed to deliver Session 19 only: Phase 10 canon and tokens, additive backend re-queue widening, shared queue primitives, and presentational QueueCard/List/EmptyDropZone components, while wiring nothing to a page and keeping routes, MCP actions, dependencies, and the E2E-wave count flat. Round 3 cannot determine whether the corrected plan would deliver that objective because the mandatory PR-6 correction census is still incomplete: none of the declared semantic variants was swept.

### Pre-Verdict Procedural Gate

`changes_required` under PR-6's procedural exception. The resubmission now contains an untruncated old/new literal census and a per-hit disposition log, but it does not contain receipts or dispositions for the semantic variants that Step 5c requires the corrector to declare **and sweep each**.

The contradiction is directly reproducible:

- `correction-census.json:3,14-142` declares 20 semantic variants across the 17 changed values.
- `run-correction-census.ps1:34-35` iterates only `old` and `new` and assigns `$terms = @($v.$dir)`; it never reads `$v.variants`.
- The reproduced index contains all 59 `old`/`new` literals but 0 of the 20 declared variants (`C:/Temp/av-kit/r3-variant-index-audit.json`).
- The correction log nevertheless claims at `2026-08-28-p10-queue-card-foundations-plan-critical-review.md:268-272` that those variants were swept as `new/1..3` rows. Those rows are later elements of each entry's `new` array, not entries from `variants`.
- Re-running the supplied driver still reports `PASS: CORRECTION_CENSUS` and `59 literals swept` despite the omission (`C:/Temp/av-kit/r3-census-rerun.txt`).

This is not a severity-rated finding. `.agent/workflows/plan-corrections.md:209-212` requires every declared semantic variant to be swept, and `.agent/workflows/plan-critical-review.md:256,288` makes a missing or undispositioned census a pre-verdict gate. Under that rule, substantive review of the corrected content is prohibited in this round.

### Round 1 Finding Resolution

The statuses below mean procedurally unresolved, not that the corrected artifacts were found defective. Content adjudication was not permitted after the PR-6 gate failed.

| Finding | Round 3 status | Evidence |
|---------|----------------|----------|
| F1 — Red oracle never constructs `$names` | `unresolved` | Not adjudicated; declared semantic variants have no census receipts or dispositions. |
| F2 — page-isolation can pass a migrated queue | `unresolved` | Not adjudicated; declared semantic variants have no census receipts or dispositions. |
| F3 — conflicting envelope extra-field contract | `unresolved` | Not adjudicated; declared semantic variants have no census receipts or dispositions. |
| F4 — WCAG oracle not bound to rendered values | `unresolved` | Not adjudicated; declared semantic variants have no census receipts or dispositions. |
| F5 — unredirected Red oracle invocations | `unresolved` | Not adjudicated; declared semantic variants have no census receipts or dispositions. |
| F6 — orphan named-set keys | `unresolved` | Not adjudicated; declared semantic variants have no census receipts or dispositions. |
| F7 — C2 labeling drift | `unresolved` | Not adjudicated; declared semantic variants have no census receipts or dispositions. |

### Findings

No severity-ranked findings were assessed. PR-6 is a pre-verdict procedural gate rather than a finding, so Round 3 `findings_count` is `0`.

### Checklist Results

#### Plan Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | not assessed | Substantive review stopped at PR-6. |
| PR-2 Not-started confirmation | not assessed | Substantive review stopped at PR-6. |
| PR-3 Task contract completeness | not assessed | Substantive review stopped at PR-6. |
| PR-4 Validation realism | not assessed | Substantive review stopped at PR-6. |
| PR-5 Source-backed planning | not assessed | Substantive review stopped at PR-6. |
| PR-6 Handoff/corrections readiness | **fail** | All 20 declared semantic variants are absent from the reproduced census index; the driver iterates only `old` and `new`. |
| PR-7 Scope discipline | not assessed | Substantive review stopped at PR-6. |
| PR-8 Control reachability and totality | not assessed | Substantive review stopped at PR-6. |
| PR-9 Single-statement discipline | not assessed | Substantive review stopped at PR-6. |

#### Documentation Review (DR)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | **fail** | The correction log says variants were swept, but the driver and index prove none was. |
| DR-2 Residual old terms | not assessed | Substantive review stopped at PR-6. |
| DR-3 Downstream references updated | not assessed | Substantive review stopped at PR-6. |
| DR-4 Verification robustness | **fail** | The driver can report PASS while omitting the entire declared `variants` surface. |
| DR-5 Evidence auditability | **fail** | No per-variant receipt or disposition exists. |
| DR-6 Cross-reference integrity | not assessed | Substantive review stopped at PR-6. |
| DR-7 Evidence freshness | pass for the evidence inspected | The reproduced driver output matches the supplied 17/59/102 summary and thereby reproduces the omission. |
| DR-8 Completion vs residual risk | pass | No implementation-complete claim was made. |

### Commands and Evidence

All process output was redirected under `C:/Temp/av-kit/`, with `$LASTEXITCODE` captured before receipt reads. No pytest, Vitest, npm test/build, Playwright, MEU status command, OpenAPI generator, product test/generator, or page-isolation `-Capture` command was run.

Key Round 3 receipts:

- `r3-census-rerun.txt` — reproduced `PASS: CORRECTION_CENSUS`, 17 values, 59 literals, and 102 sites.
- `r3-variant-index-audit.json` — 20 declared variants, 0 indexed, 20 unindexed.
- `r3-census-driver-read.txt`, `r3-census-index-read.txt`, and `r3-correction-log-full.txt` — driver/index/log evidence for the contradiction.
- `r3-predicate-census-read.txt` — the supplied structural Red-count predicate remains 8/9/13/13, all MATCH; this does not cure the missing semantic-variant sweeps.
- `r3-pre-edit-guard.json` — exact canonical write-target match.

### Required Human Direction

This is Round 3 of the configured maximum of 3. The remaining issue is **blocking**, not advisory: PR-6 prohibited substantive adjudication, so there is still no independent merits verdict on F1-F7. The round cap is now reached; correction or another review round requires explicit user direction.

### Residual Risk

The seven Round 1 corrections may be correct, but they remain independently unadjudicated. In particular, no Round 3 conclusion is made about the Red oracle, capture-then-verify isolation oracle, envelope strictness, contrast bindings/tokens, redirected Red commands, named-set binding, or C2 labels.

### Verdict

`changes_required` — the PR-6 pre-verdict gate remains unsatisfied because all 20 declared semantic variants are absent from the census receipts and disposition log. This is the final configured plan-review round, so the workflow is at a HARD STOP pending explicit user direction.


## Round 3 Corrections — Variant Sweep (corrections agent)

> Appended in response to the Round 3 PR-6 pre-verdict gate. The Round 3 finding is upheld in full,
> without qualification: the census driver never read `$v.variants`, all declared variants went
> unswept, the driver reported `PASS` anyway, and the Round 2 correction log claimed the opposite.
> This section closes all three. It records no verdict — that remains the reviewer's.

**Complete blast-radius census: 17 values changed, 82 literals swept (19 `old` + 40 `new` + 23
`variant`), 216 sites found, 64 updated, 152 confirmed consistent. Two further plan defects were
found by the variant sweep and corrected; both are the same duplicate-statement class as R1-F2/F6.**

### What was wrong and what changed

1. **Driver.** `run-correction-census.ps1` looped `foreach ($dir in @('old','new'))` and assigned
   `$terms = @($v.$dir)`. It now loops `@('old','new','variant')`, projects the `{literal, note}`
   objects in `variants` onto the same string array the other two directions use, and **hard-fails
   the run** if any declared variant carries no literal — so a silently unswept variant can no
   longer coexist with `PASS: CORRECTION_CENSUS`.
2. **Input table.** The variants had been written as prose *descriptions*, which are not
   searchable. Each is now a searchable literal plus a note stating which other form of the value
   it is. Two entries declare no variant, stated explicitly rather than left empty: `row1-deliverable`
   (a single unique sentence) and `red-counts` (structural — the predicate census counts AC rows).
3. **Correction log.** The false "were swept as `new/1..3`" claim is retracted in place above.

### Reproduction

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-28-p10-queue-card-foundations/run-correction-census.ps1 *> C:/Temp/av-kit/census-run-final.txt; $code=$LASTEXITCODE
```

Receipts: `C:/Temp/av-kit/census/census-{slug}-{old|new|variant}-{i}.txt`, one untruncated file per
swept literal; index at `C:/Temp/av-kit/census/INDEX.txt` (now carrying 23 `|variant|` rows);
run receipt `C:/Temp/av-kit/census-run-final.txt`. The index is the direct answer to the Round 3
audit: it can be re-derived with `awk -F'|' 'NR>1{s[$3]+=$6;n[$3]++}' INDEX.txt` →
`old: 19 literals / 12 sites`, `new: 40 / 92`, `variant: 23 / 112`.

### Two defects the variant sweep caught

Both were invisible to an `old`/`new` sweep, which is the entire argument for the `variants` field:

- **`page-iso-selftest / variant` (`19 cases`) — duplicate rationale.** Plan section 6 restated the
  full 17-reject / 2-accept case enumeration that `PAGE_ISOLATION_SELFTEST` already carries in
  `named-sets.json`. Two written homes for one list is the exact PR-9 defect R1-F6 raised and the
  `FROZEN_RATIONALE` correction fixed elsewhere; the sweep found the instance that correction
  missed. Collapsed to a citation — the script prints the count it actually ran, so a case added or
  dropped surfaces on the receipt. The literal now returns `rc=1`.
- **`openapi-export / variant` (`tools/export_openapi.py`) — path inlined in prose.** Section 5
  declares `OPENAPI_EXPORT` the sole generator, yet AC-41.9's observable read
  "`tools/export_openapi.py --check`" and its chain read "`export_openapi.py -o`". Rebound to the
  key. The same AC also said "`mcp-server/` has no diff" — **VCS phrasing in a tree that is not a
  git work tree**, the precise substitution R1-F2 forced everywhere else; it now asserts
  `mcp-server/src/**/*.ts` is byte-identical to its `FROZEN_GLOBS` baseline. Site count 6 → 5, all
  five survivors runnable command cells.

### Strongest confirming evidence

`red-redirect / variant` (`$LASTEXITCODE`) returns 36 sites, of which **27 are `task.md:44`–`74` —
every one of the 27 actionable rows**, with the remaining 9 in the plan's Verification Plan command
blocks. R1-F5 asked for redirected oracle invocations; the variant sweep shows immediate exit-code
capture is universal across the task table, not just present at the four rows the finding named.

### Complete per-hit disposition log (all three directions)

Every hit in every receipt carries exactly one disposition. `updated` = the site was edited during
the correction rounds; `confirmed-consistent` = the site already stated the value and still agrees.
Zero-hit literals are listed with what the absence proves. `variant` rows are new this round; `old`
and `new` rows are re-run against the current files, so the counts below supersede Round 2's.

| Value | Dir | Literal swept | rc | Sites | Disposition | Reason |
|-------|-----|---------------|----|-------|-------------|--------|
| `red-oracle-key` | old | `RED_ORACLE_CHECK` | 1 | none | n/a | no stale `RED_ORACLE_CHECK` remains in either plan file (the one surviving mention, a comment header in assert-red-oracle.ps1, was also corrected) |
| `red-oracle-key` | new | `RED_ORACLE` | 0 | `task.md:45` `task.md:48` `implementation-plan.md:76` `implementation-plan.md:79` `implementation-plan.md:82` `implementation-plan.md:85` | **updated** | the four Red rows and four WP rows now cite `RED_ORACLE`; the duplicate key is deleted |
| `red-oracle-key` | variant | `assert-red-oracle.ps1` | 0 | `implementation-plan.md:504` `implementation-plan.md:510` `task.md:44` `task.md:45` `task.md:48` `task.md:51` `task.md:54` | **confirmed-consistent** | all 7 sites are runnable validation cells (row 1 self-test + the four per-MEU Red invocations, in both the plan Verification Plan and task.md). A command cell must contain the literal path; prose cites `RED_ORACLE`. No prose site survives |
| `red-selftest` | old | `both must pass before row 2` | 1 | none | n/a | the two-precondition wording is gone |
| `red-selftest` | new | `RED_SELFTEST` | 0 | `implementation-plan.md:516` `task.md:44` | **updated** | row 1 preamble + Verification Plan now name the Red self-test as a precondition |
| `red-selftest` | new | `All three must pass before row 2` | 0 | `task.md:44` | **updated** | row 1 gate wording changed from two preconditions to three |
| `red-selftest` | new | `red-oracle-selftest.txt` | 0 | `task.md:44` | **updated** | row 1 durable outputs gained the self-test receipt |
| `red-selftest` | variant | `11 cases` | 1 | none | n/a | the Red self-test case count is stated once, as `RED_SELFTEST` ("11 hermetic fixtures"), and once more by the script itself at runtime ("PASS: RED_ORACLE selftest 11 cases"). It is never restated in plan prose, so there is nothing to drift |
| `page-iso-selftest` | old | `and run 'RED_SELFTEST'; both must pass` | 1 | none | n/a | the pre-fix row 1 preamble is gone |
| `page-iso-selftest` | new | `PAGE_ISOLATION_SELFTEST` | 0 | `task.md:44` `implementation-plan.md:569` `implementation-plan.md:573` | **updated** | row 1 + plan section 6 name the isolation self-test |
| `page-iso-selftest` | new | `-SelfTest` | 0 | `task.md:44` | **updated** | row 1 validation chain runs `-SelfTest` before `-Capture` |
| `page-iso-selftest` | new | `SELFTEST_DIR` | 0 | `implementation-plan.md:569` | **updated** | plan section 6 names the hermetic fixture root |
| `page-iso-selftest` | new | `page-iso-selftest.txt` | 0 | `task.md:44` | **updated** | row 1 durable outputs gained the self-test receipt |
| `page-iso-selftest` | variant | `19 cases` | 1 | none | n/a | CORRECTED THIS ROUND, found by the variant sweep. Plan section 6 restated the entire 17-reject / 2-accept case enumeration already carried by `PAGE_ISOLATION_SELFTEST` -- the same duplicate-rationale class as R1-F2/F6. Collapsed to a citation, so the count now has exactly one written home and the script prints what it actually ran |
| `row1-deliverable` | old | `hub bound; 'PAGE_BASELINE' captured` | 1 | none | n/a | the pre-fix deliverable wording is gone |
| `row1-deliverable` | new | `both oracle self-tests green` | 0 | `task.md:44` | **updated** | row 1 deliverable now asserts both self-tests green before the baseline |
| `e2e-count` | old | `61` | 1 | none | n/a | the wrong count 61 appears nowhere |
| `e2e-count` | new | `55` | 0 | `implementation-plan.md:270` `implementation-plan.md:287` | **confirmed-consistent** | BOTH hits are unrelated substring matches (`extra="forbid"` row and an AC-41.8 route body), NOT statements of the E2E count. The count is stated exactly once, as `E2E_BASELINE_COUNT` = 55 in named-sets.json, and is never inlined in either plan file -- which is the single-statement rule holding, not a miss |
| `e2e-count` | new | `E2E_COUNT` | 1 | none | n/a | declared variant `E2E_COUNT` does not exist -- the real key is `E2E_BASELINE_COUNT`. Recorded rather than quietly re-swept; the count itself is dispositioned above |
| `e2e-count` | new | `E2E_BASELINE_BASIS` | 0 | `implementation-plan.md:565` | **updated** | plan section 6 now cites the basis (49 in *.test.ts + 6 in *.spec.ts) instead of restating a bare number |
| `e2e-count` | new | `E2E_TITLE_SET` | 1 | none | n/a | declared variant `E2E_TITLE_SET` does not exist as a named key -- the title set lives inside `PAGE_BASELINE` and is described in plan section 6 prose |
| `e2e-count` | variant | `49` | 1 | none | n/a | the 49 + 6 split is stated once, inside `E2E_BASELINE_BASIS`, and never inlined into either plan file. Zero hits is the single-statement rule holding |
| `e2e-count` | variant | `*.spec.ts` | 1 | none | n/a | same -- the file glob lives only in the basis string |
| `envelope-policy` | old | `ignores unknown wrapper keys` | 1 | none | n/a | the "ignores unknown wrapper keys" contract is gone |
| `envelope-policy` | old | `ignore unknown wrapper keys` | 1 | none | n/a | no singular-verb variant survives either |
| `envelope-policy` | new | `ENVELOPE_UNKNOWN_KEY_POLICY` | 0 | `implementation-plan.md:348` | **updated** | AC-42.11 rewritten to assert rejection under the single named policy |
| `envelope-policy` | new | `.strict()` | 0 | `implementation-plan.md:327` `implementation-plan.md:348` | **confirmed-consistent** | Boundary Inventory (327) already required `.strict()`; AC-42.11 (348) now agrees with it instead of contradicting it |
| `envelope-policy` | variant | `extra="forbid"` | 0 | `implementation-plan.md:269` `implementation-plan.md:270` `implementation-plan.md:287` | **confirmed-consistent** | the Python-side `extra="forbid"` rule is unchanged and is asserted as unchanged by AC-41.8; it governs the FastAPI request body, `.strict()` governs the UI response envelope. Two boundaries, one rule each, no contradiction |
| `contrast-binding` | old | `hexDark` | 1 | none | n/a | the single hex pair is gone |
| `contrast-binding` | old | `hexLight` | 1 | none | n/a | the single hex pair is gone |
| `contrast-binding` | new | `STATUS_PILL_TABLE` | 0 | `task.md:46` `task.md:51` `implementation-plan.md:187` `implementation-plan.md:230` `implementation-plan.md:339` `implementation-plan.md:340` `implementation-plan.md:341` `implementation-plan.md:359` `implementation-plan.md:360` `implementation-plan.md:374` | **updated** | the pill table is now the single source for foreground/fill/alpha and is cited by the two Red rows, the testid inventory, AC-40.5, AC-42.2/42.3/42.4, the source table, and the token rationale |
| `contrast-binding` | new | `CONTRAST_BACKDROPS` | 0 | `task.md:51` `implementation-plan.md:340` `implementation-plan.md:361` | **updated** | the backdrop set is cited by AC-42.3, the both-themes source row, and the MEU-42 Red row |
| `contrast-binding` | new | `--color-pill-` | 0 | `implementation-plan.md:360` | **updated** | the ten new foreground tokens are introduced in the source-label row; they are enumerated once in `NEW_TOKENS` and authored by AC-40.3 |
| `contrast-binding` | variant | `textClass` | 0 | `task.md:51` `implementation-plan.md:339` `implementation-plan.md:341` `implementation-plan.md:342` `implementation-plan.md:374` | **confirmed-consistent** | every `textClass` site resolves through `STATUS_PILL_TABLE`; no site names a foreground class independently of the table |
| `contrast-binding` | variant | `fillClass` | 0 | `task.md:51` `implementation-plan.md:230` `implementation-plan.md:339` `implementation-plan.md:341` `implementation-plan.md:342` `implementation-plan.md:374` | **confirmed-consistent** | same for `fillClass`, including the testid/source inventory row |
| `contrast-binding` | variant | `composite` | 0 | `implementation-plan.md:340` `implementation-plan.md:360` | **confirmed-consistent** | compositing is described in exactly two places with the same meaning: AC-42.3 (the executable statement) and the source-label rationale (why the tokens exist) |
| `contrast-threshold` | old | `4.5:1` | 0 | `implementation-plan.md:150` `implementation-plan.md:360` `implementation-plan.md:361` | **confirmed-consistent** | all three are quotations of source material (the WCAG SC title at 150, the failure rationale at 360, and the proposal quote at 361), not independent contract statements. The contract site is `CONTRAST_MIN` |
| `contrast-threshold` | new | `4.60` | 0 | `implementation-plan.md:360` | **updated** | the worst surviving pairing after the ten new tokens is recorded alongside the rationale |
| `contrast-threshold` | new | `CONTRAST_MIN` | 0 | `implementation-plan.md:243` `implementation-plan.md:340` `implementation-plan.md:360` | **confirmed-consistent** | `CONTRAST_MIN` is the executable statement of the threshold and is unchanged by this round |
| `contrast-threshold` | variant | `1.4.3` | 0 | `implementation-plan.md:150` `implementation-plan.md:340` `implementation-plan.md:360` `implementation-plan.md:361` | **confirmed-consistent** | all four are SC *references* (the spec link, the AC, and two rationale rows). The threshold itself is stated once, executably, as `CONTRAST_MIN` |
| `red-redirect` | old | `assert-red-oracle.ps1 -Kind` | 0 | `implementation-plan.md:504` `implementation-plan.md:510` `task.md:45` `task.md:48` `task.md:51` `task.md:54` | **updated** | the invocation literal is unchanged by design -- what changed is that all six sites now sit inside a redirected sequence with `$LASTEXITCODE` captured immediately. Verified independently: 0 unredirected oracle invocations across 27 actionable rows |
| `red-redirect` | new | `red-oracle-meu-40.txt` | 0 | `task.md:45` `implementation-plan.md:504` | **updated** | MEU-40 oracle receipt introduced |
| `red-redirect` | new | `red-oracle-meu-41.txt` | 0 | `task.md:48` `implementation-plan.md:510` | **updated** | MEU-41 oracle receipt introduced |
| `red-redirect` | new | `red-oracle-meu-42.txt` | 0 | `task.md:51` | **updated** | MEU-42 oracle receipt introduced |
| `red-redirect` | new | `red-oracle-meu-43.txt` | 0 | `task.md:54` | **updated** | MEU-43 oracle receipt introduced |
| `red-redirect` | variant | `$LASTEXITCODE` | 0 | `implementation-plan.md:489` `implementation-plan.md:497` `implementation-plan.md:504` `implementation-plan.md:510` `implementation-plan.md:522` `implementation-plan.md:528` `implementation-plan.md:536` `implementation-plan.md:544` `implementation-plan.md:588` `task.md:44` `task.md:45` `task.md:46` `task.md:47` `task.md:48` `task.md:49` `task.md:50` `task.md:51` `task.md:52` `task.md:53` `task.md:54` `task.md:55` `task.md:56` `task.md:59` `task.md:60` `task.md:61` `task.md:62` `task.md:63` `task.md:64` `task.md:65` `task.md:66` `task.md:68` `task.md:70` `task.md:71` `task.md:72` `task.md:73` `task.md:74` | **confirmed-consistent** | the strongest evidence in this census: 27 of the 36 sites are task.md rows 44-74, i.e. every one of the 27 actionable rows captures the exit code immediately; the other 9 are the plan Verification Plan command blocks. Zero rows run a process without capture |
| `scope-labels` | old | `MEU-44+` | 0 | `task.md:40` | **confirmed-consistent** | the sole surviving `MEU-44+` is task.md:40 "Do not start MEU-44+" -- a forward-scope prohibition, a different statement from the C2 owner label R1-F7 flagged. Left deliberately |
| `scope-labels` | new | `deferred` | 0 | `implementation-plan.md:231` `implementation-plan.md:367` `implementation-plan.md:456` `implementation-plan.md:457` `implementation-plan.md:458` `implementation-plan.md:459` `implementation-plan.md:460` `implementation-plan.md:469` `implementation-plan.md:470` `implementation-plan.md:471` `implementation-plan.md:473` `implementation-plan.md:474` | **confirmed-consistent** | twelve `deferred` labels, of which the two relabeled rows (469, 470) are this round's edit and the rest predate it |
| `scope-labels` | new | `MEU-44` | 0 | `task.md:40` `implementation-plan.md:30` `implementation-plan.md:109` `implementation-plan.md:172` `implementation-plan.md:367` `implementation-plan.md:413` `implementation-plan.md:456` `implementation-plan.md:469` `implementation-plan.md:470` `implementation-plan.md:473` `implementation-plan.md:474` | **confirmed-consistent** | every `MEU-44` reference now names a concrete owner; task.md:40 is the scope guardrail, not a C2 label |
| `scope-labels` | new | `MEU-45` | 0 | `implementation-plan.md:30` `implementation-plan.md:457` `implementation-plan.md:469` | **confirmed-consistent** | `MEU-45` appears only as a concrete deferral owner |
| `scope-labels` | variant | `out-of-scope` | 0 | `implementation-plan.md:455` `implementation-plan.md:461` `implementation-plan.md:462` `implementation-plan.md:463` `implementation-plan.md:464` `implementation-plan.md:465` `implementation-plan.md:466` `implementation-plan.md:467` `implementation-plan.md:468` `implementation-plan.md:472` | **confirmed-consistent** | all 10 surviving `out-of-scope` labels are genuine C2 exclusions (plan 455-472). The two rows R1-F7 flagged (469, 470) are absent from this set -- they now read `deferred` |
| `frozen-rationale` | old | `byte-frozen for the whole session, proving` | 1 | none | n/a | the duplicated rationale prose is gone; the key is now the single statement |
| `frozen-rationale` | new | `FROZEN_RATIONALE` | 0 | `implementation-plan.md:562` | **updated** | plan section 6 now cites the key instead of restating its text |
| `frozen-rationale` | new | `byte-freezes` | 0 | `implementation-plan.md:563` | **updated** | the surviving prose is the short cited form |
| `frozen-rationale` | variant | `git diff --quiet` | 1 | none | n/a | no `git diff --quiet` guard survives anywhere in the plan files. The three VCS guards are fully absorbed into `FROZEN_GLOBS` content-freezing, which is the correct outcome in a tree that is not a git work tree |
| `frozen-rationale` | variant | `FROZEN_GLOBS` | 0 | `implementation-plan.md:288` `implementation-plan.md:563` | **updated** | the executable set is now cited at both the section 6 rationale and AC-41.9, which this round rebound from "`mcp-server/` has no diff" -- VCS phrasing in a tree that is not a work tree -- to a byte-identical check against the `FROZEN_GLOBS` baseline |
| `openapi-export` | old | `MEU-41 regenerates ('-o') because` | 0 | `implementation-plan.md:533` | **confirmed-consistent** | same line: the sentence was prefixed, not replaced, so the MEU-41 regeneration rule still reads correctly |
| `openapi-export` | new | `OPENAPI_EXPORT` | 0 | `implementation-plan.md:288` `implementation-plan.md:533` | **updated** | the generator is named rather than path-inlined in prose; the second site is AC-41.9, rebound this round by the variant sweep below |
| `openapi-export` | variant | `tools/export_openapi.py` | 0 | `task.md:49` `task.md:50` `task.md:60` `task.md:63` `implementation-plan.md:536` | **updated** | CORRECTED THIS ROUND, found by the variant sweep. Was 6 sites: AC-41.9 inlined `tools/export_openapi.py --check` and `export_openapi.py -o` in prose while section 5 declares `OPENAPI_EXPORT` the sole generator -- a PR-9 duplication. AC-41.9 now cites the key. The 5 survivors are all runnable command cells |
| `handoff-dir` | old | `MEU handoffs (first created` | 1 | none | n/a | the un-keyed H1-6 phrasing is gone |
| `handoff-dir` | new | `HANDOFF_DIR` | 0 | `task.md:65` | **updated** | H1-6 now names the directory key |
| `handoff-dir` | variant | `.agent/context/handoffs` | 0 | `task.md:47` `task.md:50` `task.md:53` `task.md:56` `task.md:64` `task.md:68` `task.md:73` | **confirmed-consistent** | all 7 sites are inside validation command cells, where the literal path is required; prose cites `HANDOFF_DIR` |
| `requeue-exhaustiveness` | old | `Chain: import the constants. Negative: the set is inlined in the guard, or duplicated` | 1 | none | n/a | the pre-fix AC-41.1 clause is gone |
| `requeue-exhaustiveness` | new | `REQUEUE_STATUS_EXHAUSTIVENESS` | 0 | `implementation-plan.md:280` | **updated** | AC-41.1 gained the partition-exhaustiveness assertion and its negative oracle |
| `requeue-exhaustiveness` | variant | `DOWNLOAD_STATUSES` | 0 | `task.md:49` `implementation-plan.md:23` `implementation-plan.md:232` `implementation-plan.md:280` `implementation-plan.md:281` `implementation-plan.md:283` `implementation-plan.md:284` `implementation-plan.md:307` | **confirmed-consistent** | the download enum appears in the constants inventory, the AC rows that partition it, and the C2 exclusion row -- every site is a consumer of the partition, none redefines it |
| `requeue-exhaustiveness` | variant | `CONVERSION_STATUSES` | 0 | `task.md:49` `implementation-plan.md:24` `implementation-plan.md:232` `implementation-plan.md:280` `implementation-plan.md:285` `implementation-plan.md:308` | **confirmed-consistent** | same for the conversion enum |
| `requeue-exhaustiveness` | variant | `NON_REQUEUEABLE_` | 0 | `implementation-plan.md:281` `implementation-plan.md:284` `implementation-plan.md:285` `implementation-plan.md:465` | **confirmed-consistent** | the complement half appears only where the partition is asserted or excluded; `REQUEUE_STATUS_EXHAUSTIVENESS` is what binds the two halves to the enums |
| `ssot-receipts` | old | `prove 'SSOT_READY'` | 0 | `task.md:62` | **confirmed-consistent** | same line: the citation was always correct, only its definition was missing |
| `ssot-receipts` | new | `SSOT_READY` | 0 | `task.md:62` | **updated** | H1-3 citation now resolves to a defined assertion receipt |
| `ssot-receipts` | new | `SSOT_APPROVED` | 0 | `task.md:71` | **updated** | H2-2 citation now resolves to a defined assertion receipt |
| `ssot-receipts` | variant | `PASS: SSOT_READY` | 0 | `task.md:62` | **confirmed-consistent** | the PASS string appears exactly once, at its owning row H1-3 |
| `ssot-receipts` | variant | `PASS: SSOT_APPROVED` | 0 | `task.md:71` | **confirmed-consistent** | the PASS string appears exactly once, at its owning row H2-2 |
| `carve-out-doorway` | old | `may contain any 'NEW_SURFACE_MODULES' string` | 1 | none | n/a | CORRECTED THIS ROUND. The census found plan section 6 still asserting the superseded substring rule ("may contain any `NEW_SURFACE_MODULES` string") one clause before the sentence saying the opposite. Rewritten to "may **resolve** an import specifier to any `NEW_SURFACE_MODULES` entry". This is exactly the regression class Step 5c exists to catch |
| `carve-out-doorway` | new | `CARVE_OUT_ALLOWED_IMPORT` | 0 | `implementation-plan.md:552` `implementation-plan.md:562` | **updated** | the allowed import is named in the carve-out rule and in the doorway narrowing |
| `carve-out-doorway` | new | `resolved suffix` | 0 | `implementation-plan.md:560` | **updated** | plan section 6 states that matching is against the resolved suffix, not the exempt directory |
| `carve-out-doorway` | variant | `re-export` | 0 | `implementation-plan.md:350` `implementation-plan.md:556` `implementation-plan.md:558` | **confirmed-consistent** | the barrel/re-export bypass class is named at the carve-out rule and twice in the resolution rationale, all consistent with resolution-based matching. Was 4 sites; the fourth was inside the duplicated self-test enumeration collapsed this round |
| `carve-out-doorway` | variant | `NEW_SURFACE_EXEMPT` | 0 | `implementation-plan.md:350` `implementation-plan.md:555` | **confirmed-consistent** | the exempt set is cited at AC-42.13 and at the section 6 doorway rule; it is defined once in named-sets.json |
| `red-counts` | old | `8/9/13/13` | 1 | none | n/a | the counts are never written as a joined literal; they are stated once each as `RED_COUNT_4x` and checked structurally by the predicate census |
| `red-counts` | new | `RED_COUNT_40` | 0 | `task.md:45` `implementation-plan.md:76` | **confirmed-consistent** | MEU-40 AC count unchanged at 8; predicate census MATCH |
| `red-counts` | new | `RED_COUNT_41` | 0 | `task.md:48` `implementation-plan.md:79` | **confirmed-consistent** | MEU-41 AC count unchanged at 9 despite the AC-41.1 rewrite; predicate census MATCH |
| `red-counts` | new | `RED_COUNT_42` | 0 | `task.md:51` `implementation-plan.md:82` | **confirmed-consistent** | MEU-42 AC count unchanged at 13 despite the F3 and F4 AC rewrites; predicate census MATCH |
| `red-counts` | new | `RED_COUNT_43` | 0 | `task.md:54` `implementation-plan.md:85` | **confirmed-consistent** | MEU-43 AC count unchanged at 13; predicate census MATCH |

---

## Round 4 Corrections - Palette Lock (corrections agent)

**Trigger: a human decision, not a reviewer finding.** Round 3 closed `changes_required` with
the variant-sweep defect fixed. Before dispatching Round 4 the user answered the two questions
the Round 3 corrections escalated:

- **Q1 (pill palette):** *"colour should be whatever it is in p:/zorivest repo"*
- **Q2 (round cap):** *"raise another 3 rounds to 6 or sooner when approved hits"*

Both are recorded as `USER_LOCKS.pill_palette` and `USER_LOCKS.plan_review_rounds`.
`PLAN_REVIEW_MAX_ROUND` is now **6**.

### What Q1 actually cost the plan

Round 2's answer to reviewer finding F4 was to **invent** ten `--color-pill-*-fg` tokens so that
all 80 pill/backdrop pairings would clear 4.5:1, yielding a designed worst case of 4.60. Q1
withdraws that entirely. The following were **deleted**, not renamed:

| Deleted | Why |
|---|---|
| ten `--color-pill-*-fg` tokens | av-kit authors no pill hue of its own |
| `--color-age-restricted` (`#c4a882`) | Zorivest has no brown; AgeRestricted takes the shared `--color-accent-red` |
| `--color-bg-selected` / `bg-bg-selected` | no such token exists in either repo; selection is an accent alpha |
| `CONTRAST_DESIGN_MARGIN` (4.60) | there is no margin to design when the palette is inherited verbatim |

### Empirical basis (this is a port, not a repaint)

All **30** `--color-*` tokens the two repos share hold **byte-identical values in both theme
blocks** - 0 mismatches. So "use Zorivest's colour" adds declarations rather than changing any
existing one. `PORTED_TOKENS` is exactly the four `--color-status-*` hexes Zorivest declares and
av-kit lacks - one of which, the light `--color-status-pending: #ea580c`, closes a gap the plan
had previously deferred.

`PILL_CLASS_RULE` is Zorivest's own canon, proven by its `a11yChipContrast` suite: a pill is
`bg-<token>/10 text-<token>` - **one** token carries both fill and foreground, and `/20` on an
accent hue is forbidden.

### The honest consequence, escalated rather than hidden

Measured from the two real stylesheets: **28 of 80 pairings clear `CONTRAST_MIN`; 52 do not**,
the light theme worst (`Paused` 2.23, `Done` 2.47). This is inherited debt - the same values
Zorivest ships - and the only fix is repointing shared token **values** app-wide, which is
neither queue-local nor an av-kit-local decision.

Rather than lower the gate or silently accept failures, **AC-42.3 was rewritten** to four
assertions: (1) the recomputed matrix equals `CONTRAST_MEASURED` exactly, ratio by ratio;
(2) every `CONTRAST_AA_PASS` pairing is >= `CONTRAST_MIN`; (3) `CONTRAST_AA_PASS` and
`CONTRAST_AA_DEBT` partition all 80 and are disjoint, so no pairing can be quietly dropped from
the audit; (4) while the debt set is non-empty, `CONTRAST_DEBT_ISSUE_ID` (`QUEUE-PILL-AA-DEBT`)
exists in `KNOWN_ISSUES_YAML` with `status: open`. Task row 3 creates it via
`CONTRAST_DEBT_ISSUE_CMD`.

**This is the plan's primary substantive question and it is put to the reviewer directly.**

### One disclosed divergence from the lock

`PILL_TOKEN_SOURCE`'s card list (`TradePlanPage.tsx:835-840`) renders selected as
`border-accent bg-accent/10` and default as `bg-bg hover:bg-bg-elevated` - byte-identical to
`CARD_STATE_CLASSES`. Its *checkbox-selected* step is `border-accent/50 bg-bg-subtle`, which is
exactly `FORBIDDEN_SELECTION_FILL` under proposal 11 conflict 5 (`--color-bg-subtle` is
`#6272a4` dark vs `#d1d5db` light, so it inverts between themes). av-kit keeps the accent-alpha
idiom at `bg-accent/5` for that step. Recorded in `SELECTION_FILL_SOURCE` and in the Spec
Sufficiency table - flagged, not silently resolved. It is a class choice, not a hue; no colour
value is av-kit-authored either way.

### Census over the correction (PR-6)

Six new values were added to `correction-census.json` (slugs prefixed `r4-`) and the whole
census re-run in all three directions.

```
Blast-radius census: 23 values changed, 132 literals swept (old+new+variant), 277 sites found.
  predicate 40|8|8|MATCH
  predicate 41|9|9|MATCH
  predicate 42|13|13|MATCH
  predicate 43|13|13|MATCH
PASS: CORRECTION_CENSUS   EXIT=0
```

Transitive binding census re-run after the key deletions/additions:
`top-level keys: 178 | bound: 178 | UNBOUND: 0` / `DANGLING citations: 0`.

Two census literals were **wrong on the first pass and are reported rather than quietly fixed**:
a bare `/20` matched 32 sites, nearly all of them `/2026-...` date paths, so it was replaced by
the nine concrete forbidden classes (`accent-cyan/20` ... `status-canceled/20`), each of which
must return rc=1; and `/20 on an accent` returned rc=1 only because the plan backticks the alpha,
which `rg -F` cannot match through, so it was restated as `on an accent hue is forbidden` and now
returns rc=0 at plan:360.

### Per-hit disposition log (R4 values, all three directions)

rg exit codes: 0 = matched, 1 = no match, >1 = real error. For an `old` literal rc=1 is the good
outcome; for a `new` literal rc=0 is. Every row below is dispositioned.

| slug | dir | i | rc | hits | literal | disposition |
|---|---|---|---|---|---|---|
| `r4-pill-fg-tokens` | old | 0 | 0 | 1 | `--color-pill-` | confirmed-consistent - the surviving hit is a supersession/retraction note, not a live rule |
| `r4-pill-fg-tokens` | old | 1 | 1 | 0 | `fgToken` | **updated** - 0 stale sites remain |
| `r4-pill-fg-tokens` | old | 2 | 1 | 0 | `fillToken` | **updated** - 0 stale sites remain |
| `r4-pill-fg-tokens` | old | 3 | 1 | 0 | `NEW_TOKENS` | **updated** - 0 stale sites remain |
| `r4-pill-fg-tokens` | new | 0 | 0 | 9 | `PILL_TOKEN_SOURCE` | **updated** - the edit landed |
| `r4-pill-fg-tokens` | new | 1 | 0 | 3 | `PILL_CLASS_RULE` | **updated** - the edit landed |
| `r4-pill-fg-tokens` | new | 2 | 0 | 6 | `PORTED_TOKENS` | **updated** - the edit landed |
| `r4-pill-fg-tokens` | new | 3 | 0 | 8 | `USER_LOCKS.pill_palette` | **updated** - the edit landed |
| `r4-pill-fg-tokens` | variant | 0 | 0 | 1 | `bg-accent-red/10` | confirmed-consistent - present as required |
| `r4-pill-fg-tokens` | variant | 1 | 1 | 0 | `text-accent-red` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-pill-fg-tokens` | variant | 2 | 0 | 1 | `on an accent hue is forbidden` | confirmed-consistent - present as required |
| `r4-pill-fg-tokens` | variant | 3 | 1 | 0 | `accent-cyan/20` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-pill-fg-tokens` | variant | 4 | 1 | 0 | `accent-yellow/20` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-pill-fg-tokens` | variant | 5 | 1 | 0 | `accent-purple/20` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-pill-fg-tokens` | variant | 6 | 1 | 0 | `accent-orange/20` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-pill-fg-tokens` | variant | 7 | 1 | 0 | `accent-red/20` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-pill-fg-tokens` | variant | 8 | 1 | 0 | `status-pending/20` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-pill-fg-tokens` | variant | 9 | 1 | 0 | `status-filled/20` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-pill-fg-tokens` | variant | 10 | 1 | 0 | `status-rejected/20` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-pill-fg-tokens` | variant | 11 | 1 | 0 | `status-canceled/20` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-age-restricted` | old | 0 | 0 | 1 | `--color-age-restricted` | confirmed-consistent - the surviving hit is a supersession/retraction note, not a live rule |
| `r4-age-restricted` | old | 1 | 0 | 1 | `#c4a882` | confirmed-consistent - the surviving hit is a supersession/retraction note, not a live rule |
| `r4-age-restricted` | new | 0 | 0 | 3 | `--color-accent-red` | **updated** - the edit landed |
| `r4-age-restricted` | new | 1 | 0 | 1 | `bg-accent-red/10` | **updated** - the edit landed |
| `r4-age-restricted` | variant | 0 | 0 | 2 | `Brown` | confirmed-consistent - present as required |
| `r4-bg-selected` | old | 0 | 0 | 1 | `--color-bg-selected` | confirmed-consistent - the surviving hit is a supersession/retraction note, not a live rule |
| `r4-bg-selected` | old | 1 | 1 | 0 | `bg-bg-selected` | **updated** - 0 stale sites remain |
| `r4-bg-selected` | new | 0 | 0 | 1 | `SELECTION_FILL_SOURCE` | **updated** - the edit landed |
| `r4-bg-selected` | new | 1 | 0 | 1 | `bg-accent/10` | **updated** - the edit landed |
| `r4-bg-selected` | variant | 0 | 0 | 1 | `bg-accent/5` | confirmed-consistent - present as required |
| `r4-bg-selected` | variant | 1 | 0 | 3 | `FORBIDDEN_SELECTION_FILL` | confirmed-consistent - present as required |
| `r4-contrast-baseline` | old | 0 | 1 | 0 | `4.60` | **updated** - 0 stale sites remain |
| `r4-contrast-baseline` | old | 1 | 1 | 0 | `CONTRAST_DESIGN_MARGIN` | **updated** - 0 stale sites remain |
| `r4-contrast-baseline` | new | 0 | 0 | 2 | `CONTRAST_MEASURED` | **updated** - the edit landed |
| `r4-contrast-baseline` | new | 1 | 0 | 1 | `CONTRAST_AA_PASS` | **updated** - the edit landed |
| `r4-contrast-baseline` | new | 2 | 0 | 1 | `CONTRAST_AA_DEBT` | **updated** - the edit landed |
| `r4-contrast-baseline` | variant | 0 | 1 | 0 | `contrast-matrix.json` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-contrast-baseline` | variant | 1 | 0 | 2 | `80 pairings` | confirmed-consistent - present as required |
| `r4-contrast-baseline` | variant | 2 | 0 | 2 | `CONTRAST_MIN` | confirmed-consistent - present as required |
| `r4-debt-followup` | old | 0 | 1 | 0 | `known-issues.md entry` | **updated** - 0 stale sites remain |
| `r4-debt-followup` | new | 0 | 0 | 2 | `CONTRAST_DEBT_ISSUE_ID` | **updated** - the edit landed |
| `r4-debt-followup` | new | 1 | 0 | 2 | `CONTRAST_DEBT_ISSUE_CMD` | **updated** - the edit landed |
| `r4-debt-followup` | new | 2 | 0 | 2 | `KNOWN_ISSUES_YAML` | **updated** - the edit landed |
| `r4-debt-followup` | new | 3 | 0 | 2 | `KNOWN_ISSUES_MD` | **updated** - the edit landed |
| `r4-debt-followup` | variant | 0 | 1 | 0 | `QUEUE-PILL-AA-DEBT` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-debt-followup` | variant | 1 | 0 | 1 | `CONTRAST_DEBT_FOLLOWUP` | confirmed-consistent - present as required |
| `r4-round-cap` | old | 0 | 1 | 0 | `"PLAN_REVIEW_MAX_ROUND": 3` | **updated** - 0 stale sites remain |
| `r4-round-cap` | new | 0 | 1 | 0 | `"PLAN_REVIEW_MAX_ROUND": 6` | **absent by design** - the value lives in `named-sets.json`, outside the swept scope (proves it is stated once) |
| `r4-round-cap` | variant | 0 | 1 | 0 | `maximum of 3` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r4-round-cap` | variant | 1 | 0 | 1 | `PLAN_REVIEW_MAX_ROUND` | confirmed-consistent - present as required |

**R4 totals: 50 literals swept, 62 sites found, every row dispositioned.**
Untruncated receipts: `C:/Temp/av-kit/census/census-r4-*.txt`; index at
`C:/Temp/av-kit/census/INDEX.txt`.

### Files changed this round

- `named-sets.json` - 178 bound keys. Added `PILL_TOKEN_SOURCE`, `PILL_CLASS_RULE`,
  `PORTED_TOKENS`, `CONTRAST_MEASURED`, `CONTRAST_AA_PASS`, `CONTRAST_AA_DEBT`,
  `CONTRAST_DEBT_FOLLOWUP`, `CONTRAST_DEBT_ISSUE_ID`, `CONTRAST_DEBT_ISSUE_CMD`,
  `KNOWN_ISSUES_YAML`, `KNOWN_ISSUES_MD`, `SELECTION_FILL_SOURCE`; rewrote `STATUS_PILL_TABLE`
  and `CONTRAST_RULE`; deleted `NEW_TOKENS` and `CONTRAST_DESIGN_MARGIN`;
  `PLAN_REVIEW_MAX_ROUND` 3 -> 6; `USER_LOCKS` gains `pill_palette` and `plan_review_rounds`
- `contrast-matrix.json` - **new**, the 80-row measured baseline (`pass: 28`, `debt: 52`)
- `implementation-plan.md` - AC-40.3, AC-40.5, AC-41.9, AC-42.2, AC-42.3, AC-42.4, three Spec
  Sufficiency rows, WP-40b, and section 6
- `task.md` - rows 3 and 8
- `correction-census.json` + `run-correction-census.ps1` - six R4 values added; the driver is
  unchanged since Round 3

**Verdict authorship unchanged:** this section is the corrections agent's record. It asserts no
verdict. Round 4's verdict is the external reviewer's alone.

## Round 4

### Intent Anchor

Executing this plan should establish a queue-card foundation that preserves every useful queue
operation, tells the truth about the scope of destructive actions, makes blocker states recoverable,
and keeps status text readable in both themes. It does not yet meet that objective: the control
inventory is directionally sound, but five product-contract defects would produce unreadable pills,
an invalid retry path, misleading or ambiguous actions, or inconsistent partial deletion.

### Findings

| Finding | Severity | Confidence | Wrong delivered behavior | Evidence | Recommendation |
|---|---|---|---|---|---|
| F1 | **High** | High | **The chosen class rule knowingly ships status text that is unreadable in ordinary light-theme states.** The measured baseline has 52/80 failures; only two light-theme pairings pass, with common labels such as Paused and Done falling to 2.23:1 and 2.47:1. A local desktop app gets no accessibility exemption, and an open debt issue does not make the rendered label readable. | `implementation-plan.md:339-361`; `named-sets.json:456-590,644-696`; `contrast-matrix.json:3-5,288-565`; Zorivest `globals.css:126-167` | Read the human lock as **Zorivest's hues/tokens**, not as a lock to Zorivest's same-token foreground class. Keep the exact Zorivest status hue on the 10% fill and status icon, use Zorivest's theme `text-fg` (or another measured Zorivest foreground role) for the label, and restore an all-pairings >=4.5 gate. Do **not** repoint shared token values app-wide. |
| F2 | **High** | High | **Retry from `QualityBlocked` bypasses the condition that created the block, and blocker-state Retry is context-free.** With SABR still active, an incompatible job can be reset to Pending with the same quality; the worker selects every Pending job and does not re-run `apply_lock` before `_run_one`, so Retry defeats the quality guard. `AgeRestricted` is reasonably retryable after cookie settings change, but the card contract does not require any remediation copy, so an unchanged Retry can look broken. | `implementation-plan.md:280-288,315-317,408-410`; `packages/core/src/avkit_core/domain/download.py:28-48,121-129`; `packages/core/src/avkit_core/services/download.py:351-391,409-424,460-505` | Preserve the human's widened Retry scope, but special-case blocker states: QualityBlocked Retry must apply current compatible defaults and revalidate active SABR (otherwise remain blocked/409); AgeRestricted Retry may re-enter after settings change. Require the card meta to show the blocker reason and the setting the user must change before retrying. |
| F3 | **High** | High | **A row-local Cancel control is not required to disclose that it stops the queue processor.** The callback is named `onCancelQueue`, but the plan permits the user-facing accessible name/title to be merely “Cancel.” A person acting on one row can therefore stop the queue while reasonably believing only that item is affected. The mockup was more honest than the AC: its tooltip explicitly says queue-level. | `implementation-plan.md:194-200,408-410`; `named-sets.json:263-267,288-294`; `2026-08-27-queue-card-ui-mockup.html:269,287,442` | Keep the human-selected row placement and no-dialog behavior, but lock and test the exact scope-bearing name/title, e.g. **“Cancel queue”** / “Cancel queue - this is the in-flight item.” Do not allow a bare “Cancel” label. |
| F4 | **High** | High | **Clear finished has a destination set but no complete partial-failure behavior.** “G35 partial-result toast” does not say whether the fan-out continues after one DELETE fails, whether successes remain removed, or how stale/raced jobs are reconciled. An implementation can stop on the third request, leave later Done jobs unattempted, and still claim a partial-result toast. | `implementation-plan.md:231,458`; `named-sets.json:288-295`; `2026-08-27-queue-card-ui-proposal.md:122-125,135,223-225` | Put the product semantics in the canon now: snapshot Done IDs; attempt every deletion independently and continue after per-item failure; never delete files; refetch once; preserve confirmed successes; and report removed/failed-or-skipped counts plus reasons. Add the exact AC in MEU-46 when wired. |
| F5 | **Medium** | High | **The kebab contract can produce dead actions or incompatible implementations.** The prop contract says missing callbacks hide controls, while AC-43.8 says every menu contains exactly all eight `KEBAB_MENU_ORDER` entries. A Pending first row can therefore either show unusable Open file / Move up actions, omit them and fail the AC, or render no-op buttons. | `implementation-plan.md:396,412-413`; `named-sets.json:270-279` | Define `KEBAB_MENU_ORDER` as the relative order of **applicable supplied actions**, then specify state/boundary availability (for example no Open file before a path exists, no Move up at the top). Missing callbacks must omit the action; no no-op menu items. |

### Direct Recommendation on the Palette Lock

Do **not** ship the 52 sub-AA pairings, and do **not** repoint shared token values app-wide in this
queue-foundation plan. Port Zorivest's hue tokens verbatim for the status fill/icon, but decouple the
label foreground and use a theme foreground role that passes 4.5:1. “Use Zorivest's colour” is
faithfully satisfied by Zorivest's token values and visual hue; it does not require copying a class
combination whose measured result is inaccessible.

The current pass/debt partition itself is not laundering: reproduced static evidence is 80 matrix
rows = 28 pass + 52 debt, with zero overlap, missing, or extra rows and zero declared-pass rows below
4.5 (`C:/Temp/av-kit/r4-contrast-partition-audit.txt`). Moving a pairing from debt to pass without a
ratio improvement fails the separate pass-threshold assertion. The partition is an honest audit of a
bad shipping decision, not a remedy for it.

### Other Substantive Judgments

- **Control reduction:** The 13-to-4-plus-overflow model retains the needed operations: processor
  start/pause/resume remain global; Retry/Open/Cancel become state-dependent card actions; reorder,
  remove, open-folder, and copy move into the kebab/bulk surface; Clear all remains in overflow.
  F3 and F5 are the remaining truthfulness/applicability defects, not missing toolbar reachability.
- **Re-queue widening:** Failed and Cancelled -> Pending are sound. AgeRestricted -> Pending is sound
  after cookie/auth settings can change because download options are read at execution time.
  QualityBlocked -> Pending is sound only with the compatibility recheck described in F2; unconditional
  generic reset is not.
- **Scope honesty:** MEU-40..43 genuinely deliver canon, backend widening, primitives, and
  presentational components without page wiring. The two queue-table edits are helper-import-only and
  do not smuggle migration into this session. Toolbar, selection, Clear finished wiring, and page E2E
  remain explicitly deferred.
- **Selection-fill divergence:** `bg-accent/5` is the right call. Zorivest's `bg-bg-subtle` selection
  fill changes semantic character across themes; av-kit's accent tint preserves selection meaning,
  and the checked checkbox plus border keeps selection from being color-only.

### Round 3 Resolution and Permitted Evidence

Round 3's variant-sweep defect is treated as closed per the human's instruction and the correction
record; it was not re-litigated. The two permitted hermetic controls were reproduced:

- `assert-red-oracle.ps1 -SelfTest` -> `PASS: RED_ORACLE selftest 11 cases`
  (`C:/Temp/av-kit/r4-red-selftest.txt`).
- `assert-page-isolation.ps1 -SelfTest` -> `PASS: PAGE_ISOLATION selftest 19 cases`
  (`C:/Temp/av-kit/r4-iso-selftest.txt`).

No pytest, Vitest, npm test/build, Playwright, MEU-status command, OpenAPI export, issue-triage
command, product generator, or real-tree page-isolation capture was run. Every `task.md` row remains
unchecked and all four planned MEU handoffs are absent, confirming plan-review mode.

### Checklist Results

| Product check | Result | Evidence |
|---|---|---|
| Readable and honest status system | **fail** | F1; 52/80 pairings below 4.5. |
| Action scope matches what the user sees | **fail** | F3; queue-level cancellation is not locked into the control's label/title. |
| Retry preserves backend invariants | **fail** | F2; QualityBlocked can bypass the active compatibility lock. |
| Fan-out behavior is deterministic under partial failure | **fail** | F4; continuation and reconciliation are unspecified. |
| All secondary actions are reachable and applicable | **partial** | Inventory is complete, but F5 leaves applicability contradictory. |
| Foundation-only scope is honest | pass | No page migration is scheduled; migration and E2E waves are deferred to named MEUs. |
| Selection state works in both themes | pass | Accent tint plus border/checkbox is semantically stable and non-color-only. |
| Contrast audit resists simple relabeling | pass | 80/28/52 exact partition; pass rows independently enforce 4.5. |

### Residual Risk

After F1-F5 are corrected, the main deferred risk is migration quality: the presentational contract
will not be proven in real Electron until MEU-44 mounts it. That deferral is honest for this session,
but the migration tests must verify the exact Cancel-queue wording, blocker remediation copy, filtered
kebab actions, and Clear-finished partial-result behavior rather than only component callbacks.

### Verdict

`changes_required` - five Round 4 product findings. The palette baseline and debt partition are
truthful, but knowingly shipping 52 unreadable combinations is not acceptable; use Zorivest hues
with an accessible foreground instead of copying its same-token pill class. The QualityBlocked retry
bypass and the destructive/action-semantics gaps must also be corrected before implementation.

---

## Round 5 Corrections - Reviewer F1-F5 (corrections agent)

Round 4 returned `changes_required` with **five substantive product findings and zero procedural
findings** - the refocus the user asked for worked. All five are accepted; none is argued down.

| F | Sev | Wrong behaviour it named | Disposition |
|---|---|---|---|
| F1 | High | Same-token pill ships 52/80 unreadable label states (light `Paused` 2.23, `Done` 2.47) | **Accepted in full.** Label decoupled to `--color-fg`; 80/80 now clear `CONTRAST_MIN` |
| F2 | High | QualityBlocked Retry bypasses the compatibility lock; blocker Retry is context-free | **Accepted in full.** `REQUEUE_BLOCKER_POLICY` + AC-41.10 + AC-43.15 |
| F3 | High | A row-local control named `Cancel` stops the whole queue | **Accepted in full.** `CANCEL_SCOPE_RULE` + AC-43.14 |
| F4 | High | Clear-finished had no complete partial-failure behaviour | **Accepted in full.** `CLEAR_FINISHED_SEMANTICS`, seven clauses, into canon via AC-40.6 |
| F5 | Med | Kebab can render dead actions | **Accepted in full.** `KEBAB_MENU_ORDER_SEMANTICS` + `KEBAB_AVAILABILITY`, AC-43.8 rewritten |

### F1 - the remedy was measured before it was written

The reviewer's recommendation was to read `USER_LOCKS.pill_palette` as **Zorivest's hues**, not as
Zorivest's class *combination*. Three candidate label foregrounds were measured across all 80
pairings from the two real stylesheets before choosing:

| label foreground | pass | worst |
|---|---|---|
| the fill token itself (R4's rule) | 28/80 | 1.82 |
| `--color-fg-muted` | 80/80 | 5.31 |
| **`--color-fg`** (chosen) | **80/80** | **6.61** (`dark/Paused/hover`) |

Two facts make this a port rather than a repaint, and both were verified rather than assumed:

1. `--color-fg` is one of the **30** tokens the two repos hold **byte-identical** (`#f8f8f2` dark /
   `#1e293b` light). Taking the label from it authors no av-kit hue, so the lock still holds in full.
2. The proposal's own mockup **already decouples fill from foreground**:
   `.pill.red { background: rgba(255,85,85,.18); color: #ff9e9e; }` (mockup:151). The decoupling is
   therefore **Spec-backed, not a deviation** - R4's same-token reading was the deviation.

Shared token **values** are untouched: no app-wide repoint, which was the blast radius the reviewer
warned against. The status **icon** keeps the hue (`iconClass`), and its 80 icon-vs-fill ratios are
recorded in `contrast-matrix.json` as **advisory** - 12 fall below 3.0, permitted under WCAG 1.4.11's
Decorative exception because the icon is `aria-hidden="true"` and fully redundant with the pill's own
text label (`STATUS_ICON_RULE`). The numbers are recorded rather than omitted so a future change
cannot quietly make the icon load-bearing.

**The entire debt apparatus is deleted, not re-tuned**: `CONTRAST_AA_PASS`, `CONTRAST_AA_DEBT`,
`CONTRAST_DEBT_FOLLOWUP`, `CONTRAST_DEBT_ISSUE_ID`, `CONTRAST_DEBT_ISSUE_CMD`, `KNOWN_ISSUES_YAML`,
`KNOWN_ISSUES_MD`, and the `QUEUE-PILL-AA-DEBT` known-issue that task row 3 would have opened. There
is no debt, so there is nothing to track. AC-42.3 is now two unconditional assertions - all 80 label
pairings >= `CONTRAST_MIN`, and exact ratio-by-ratio match against `CONTRAST_MEASURED` - with a
fourth negative oracle that sets a `labelClass` back to its own hue and requires the suite to go red.

**Interpretive call, disclosed for the Step 5c gate:** the user said colour comes from Zorivest. This
reads that as Zorivest's *token values*, not Zorivest's *class combination*. If the user meant the
class combination literally, the plan ships 52 sub-AA label states and F1 stands unfixed.

### F2 - verified against the service, not assumed

The reviewer's claim was checked in source before writing the policy. `services/download.py`
`apply_lock()` only ever transitions **Pending -> QualityBlocked**, and `_run_one` (line 489) does
**not** re-run it. So a generic reset drops a QualityBlocked job into the same Pending pool the
worker drains - Retry would defeat the guard that created the block. `REQUEUE_BLOCKER_POLICY` now
requires `QualityBlocked -> Pending` to apply the current downloader defaults and re-evaluate
`_incompatible(job)` against the live SABR snapshot, answering `REQUEUE_BLOCKER_CONFLICT_CODE` (409)
with `BLOCKER_REMEDIATION['QualityBlocked']` when it is still incompatible. `AgeRestricted` re-queues
unconditionally - cookie/auth options are read at execution time, so a settings change suffices.
AC-43.15 pairs with it so the refusal a user can hit is the refusal the card explains.

### F3 / F4 / F5

- **F3:** `CANCEL_CONTROL_LABEL` = `Cancel queue`, `CANCEL_CONTROL_TITLE` =
  `Cancel queue - this is the in-flight item`, `CANCEL_LABEL_FORBIDDEN` = the four misleading bare
  strings. AC-43.14 asserts the accessible name by equality and requires the same scope wording in
  the confirm step. The mockup's own tooltip (mockup:287) was already scope-bearing; the AC now
  matches it instead of under-specifying it.
- **F4:** `CLEAR_FINISHED_SEMANTICS` fixes seven clauses - snapshot before the first request,
  independent attempts, **continue after failure**, successes never rolled back, never delete media
  from disk, exactly one reconciling refetch, and a `G35_RULE` toast reporting removed/failed counts
  plus a reason per failure. AC-40.6 requires every clause in canon, so the deferred MEU-46
  implementation inherits a complete contract rather than "partial-result toast".
- **F5:** `KEBAB_MENU_ORDER` is now explicitly a **relative order over applicable supplied actions**.
  `KEBAB_AVAILABILITY` gives a condition for each of the eight labels; an inapplicable action is
  **absent from the DOM**, never disabled and never a no-op. AC-43.8 asserts three cases: a mid-list
  `Done` job (all eight), a **first-row `Pending`** job (`Copy path` + `Remove` only), and a card
  given only `onRemove`.

  While writing this, `KEBAB_AVAILABILITY`'s keys were found to be a different vocabulary from
  `KEBAB_MENU_ORDER`'s eight labels (it had `copy-url`/`copy-error`, and lacked `Move to bottom`).
  **Reported rather than quietly patched:** the map is now keyed 1:1 on `KEBAB_MENU_ORDER`, asserted
  in the generator.

### Census over the correction (PR-6)

Seven `r5-` values added; the whole census re-run in all three directions.

```
Blast-radius census: 30 values changed, 189 literals swept (old+new+variant), 345 sites found.
  predicate 40|8|8|MATCH
  predicate 41|10|10|MATCH
  predicate 42|13|13|MATCH
  predicate 43|15|15|MATCH
PASS: CORRECTION_CENSUS   EXIT=0
```

`RED_COUNT_41` 9 -> **10** (AC-41.10) and `RED_COUNT_43` 13 -> **15** (AC-43.14, AC-43.15); the
predicate census counts AC rows in the plan, so a declared count that drifts from the table fails.

Transitive binding census after the key deletions and additions:
`top-level keys: 185 | bound: 185 | UNBOUND: 0` / `DANGLING citations: 0`.

One census literal was **mis-declared and is reported, not silently dropped**:
`isInFlight` is true, and clicking it invokes`` was declared an `old` literal, implying AC-43.5 should
disappear. It should not - AC-43.5 asserts the *wiring* and is retained; AC-43.14 adds the *wording*
on top. It was reclassified as a `variant` whose pass condition is rc=0.

### Per-hit disposition log (R5 values, all three directions)

rg exit codes: 0 = matched, 1 = no match, >1 = real error. For an `old` literal rc=1 is the good
outcome; for a `new` literal rc=0 is. Every row below is dispositioned.

| slug | dir | i | rc | hits | literal | disposition |
|---|---|---|---|---|---|---|
| `r5-pill-label-fg` | old | 0 | 1 | 0 | `textClass` | **updated** - 0 stale sites remain |
| `r5-pill-label-fg` | old | 1 | 1 | 0 | `carrying **both** fill and foreground` | **updated** - 0 stale sites remain |
| `r5-pill-label-fg` | new | 0 | 0 | 6 | `labelClass` | **updated** - the edit landed |
| `r5-pill-label-fg` | new | 1 | 0 | 5 | `iconClass` | **updated** - the edit landed |
| `r5-pill-label-fg` | new | 2 | 0 | 3 | `text-fg` | **updated** - the edit landed |
| `r5-pill-label-fg` | variant | 0 | 1 | 0 | `the Tailwind form of the **same** `token`` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r5-pill-label-fg` | variant | 1 | 0 | 4 | ``--color-fg`` | confirmed-consistent - present as required |
| `r5-pill-label-fg` | variant | 2 | 0 | 4 | `PILL_CLASS_RULE` | confirmed-consistent - present as required |
| `r5-contrast-all-pass` | old | 0 | 1 | 0 | `CONTRAST_AA_PASS` | **updated** - 0 stale sites remain |
| `r5-contrast-all-pass` | old | 1 | 1 | 0 | `CONTRAST_AA_DEBT` | **updated** - 0 stale sites remain |
| `r5-contrast-all-pass` | old | 2 | 1 | 0 | `CONTRAST_DEBT_FOLLOWUP` | **updated** - 0 stale sites remain |
| `r5-contrast-all-pass` | old | 3 | 1 | 0 | `CONTRAST_DEBT_ISSUE_ID` | **updated** - 0 stale sites remain |
| `r5-contrast-all-pass` | old | 4 | 1 | 0 | `CONTRAST_DEBT_ISSUE_CMD` | **updated** - 0 stale sites remain |
| `r5-contrast-all-pass` | old | 5 | 1 | 0 | `KNOWN_ISSUES_YAML` | **updated** - 0 stale sites remain |
| `r5-contrast-all-pass` | old | 6 | 1 | 0 | `KNOWN_ISSUES_MD` | **updated** - 0 stale sites remain |
| `r5-contrast-all-pass` | old | 7 | 0 | 1 | `28 of 80` | confirmed-consistent - the sole surviving hit is the retraction sentence in the Spec Sufficiency table that narrates what R4 measured before withdrawing it |
| `r5-contrast-all-pass` | old | 8 | 1 | 0 | `QUEUE-PILL-AA-DEBT` | **updated** - 0 stale sites remain |
| `r5-contrast-all-pass` | new | 0 | 0 | 2 | `CONTRAST_WORST_MEASURED` | **updated** - the edit landed |
| `r5-contrast-all-pass` | new | 1 | 0 | 2 | `STATUS_ICON_RULE` | **updated** - the edit landed |
| `r5-contrast-all-pass` | new | 2 | 0 | 1 | `80 of 80` | **updated** - the edit landed |
| `r5-contrast-all-pass` | variant | 0 | 1 | 0 | `52 do not` | confirmed-consistent - absent as required (rc=1 *is* the pass condition for a forbidden form) |
| `r5-contrast-all-pass` | variant | 1 | 0 | 1 | `pass/debt partition` | confirmed-consistent - AC-42.3 now reads "There is no pass/debt partition"; the phrase survives only as its own negation |
| `r5-contrast-all-pass` | variant | 2 | 0 | 1 | `CONTRAST_MEASURED` | confirmed-consistent - present as required |
| `r5-contrast-all-pass` | variant | 3 | 0 | 1 | `advisory` | confirmed-consistent - present as required |
| `r5-blocker-requeue` | old | 0 | 1 | 0 | `reset_failed is only valid from Failed` | **updated** - 0 stale sites remain |
| `r5-blocker-requeue` | new | 0 | 0 | 3 | `REQUEUE_BLOCKER_POLICY` | **updated** - the edit landed |
| `r5-blocker-requeue` | new | 1 | 0 | 2 | `REQUEUE_BLOCKER_CONFLICT_CODE` | **updated** - the edit landed |
| `r5-blocker-requeue` | new | 2 | 0 | 1 | `BLOCKER_STATUSES` | **updated** - the edit landed |
| `r5-blocker-requeue` | new | 3 | 0 | 4 | `BLOCKER_REMEDIATION` | **updated** - the edit landed |
| `r5-blocker-requeue` | new | 4 | 0 | 2 | `BLOCKER_META_RULE` | **updated** - the edit landed |
| `r5-blocker-requeue` | new | 5 | 0 | 4 | `AC-41.10` | **updated** - the edit landed |
| `r5-blocker-requeue` | new | 6 | 0 | 1 | `AC-43.15` | **updated** - the edit landed |
| `r5-blocker-requeue` | variant | 0 | 0 | 2 | `_incompatible` | confirmed-consistent - present as required |
| `r5-blocker-requeue` | variant | 1 | 0 | 2 | `apply_lock` | confirmed-consistent - present as required |
| `r5-blocker-requeue` | variant | 2 | 0 | 2 | `_run_one` | confirmed-consistent - present as required |
| `r5-cancel-wording` | new | 0 | 0 | 3 | `CANCEL_CONTROL_LABEL` | **updated** - the edit landed |
| `r5-cancel-wording` | new | 1 | 0 | 2 | `CANCEL_CONTROL_TITLE` | **updated** - the edit landed |
| `r5-cancel-wording` | new | 2 | 0 | 2 | `CANCEL_LABEL_FORBIDDEN` | **updated** - the edit landed |
| `r5-cancel-wording` | new | 3 | 0 | 3 | `CANCEL_SCOPE_RULE` | **updated** - the edit landed |
| `r5-cancel-wording` | new | 4 | 0 | 1 | `AC-43.14` | **updated** - the edit landed |
| `r5-cancel-wording` | variant | 0 | 0 | 1 | `Cancel queue` | confirmed-consistent - present as required |
| `r5-cancel-wording` | variant | 1 | 0 | 2 | `per-item cancel` | confirmed-consistent - present as required |
| `r5-cancel-wording` | variant | 2 | 0 | 1 | `isInFlight` is true, and clicking it invokes` | confirmed-consistent - AC-43.5 (wiring) is RETAINED; AC-43.14 adds the wording requirement on top. **Mis-declared as an `old` literal on the first R5 pass and reclassified rather than silently dropped** |
| `r5-clear-finished` | old | 0 | 1 | 0 | `Done-only Clear finished with files retained. Chain` | **updated** - 0 stale sites remain |
| `r5-clear-finished` | new | 0 | 0 | 1 | `CLEAR_FINISHED_SEMANTICS` | **updated** - the edit landed |
| `r5-clear-finished` | variant | 0 | 0 | 4 | `snapshot` | confirmed-consistent - present as required |
| `r5-clear-finished` | variant | 1 | 1 | 0 | `continue_on_failure` | **absent by design** - the clause is stated in prose ("a failure never aborts the remaining ids"); the JSON key itself lives in `named-sets.json`, outside the swept scope |
| `r5-clear-finished` | variant | 2 | 0 | 1 | `G35_RULE` | confirmed-consistent - present as required |
| `r5-kebab-applicability` | old | 0 | 1 | 0 | `with exactly `KEBAB_MENU_ORDER` in that order` | **updated** - 0 stale sites remain |
| `r5-kebab-applicability` | new | 0 | 0 | 2 | `KEBAB_MENU_ORDER_SEMANTICS` | **updated** - the edit landed |
| `r5-kebab-applicability` | new | 1 | 0 | 2 | `KEBAB_AVAILABILITY` | **updated** - the edit landed |
| `r5-kebab-applicability` | variant | 0 | 0 | 1 | `never rendered disabled` | confirmed-consistent - present as required |
| `r5-kebab-applicability` | variant | 1 | 0 | 5 | `KEBAB_MENU_ORDER` | confirmed-consistent - present as required |
| `r5-red-counts` | old | 0 | 1 | 0 | `"RED_COUNT_41": 9` | **updated** - 0 stale sites remain |
| `r5-red-counts` | old | 1 | 1 | 0 | `"RED_COUNT_43": 13` | **updated** - 0 stale sites remain |
| `r5-red-counts` | new | 0 | 1 | 0 | `"RED_COUNT_41": 10` | **absent by design** - the value is stated once in `named-sets.json`, outside the swept scope |
| `r5-red-counts` | new | 1 | 1 | 0 | `"RED_COUNT_43": 15` | **absent by design** - the value is stated once in `named-sets.json`, outside the swept scope |

**R5 totals: 57 literals swept, 85 sites found, every row dispositioned.**
Untruncated receipts: `C:/Temp/av-kit/census/census-r5-*.txt`; index at
`C:/Temp/av-kit/census/INDEX.txt`.

### Files changed this round

- `named-sets.json` - **185** bound keys. Added `STATUS_ICON_RULE`, `CONTRAST_WORST_MEASURED`,
  `REQUEUE_BLOCKER_POLICY`, `REQUEUE_BLOCKER_CONFLICT_CODE`, `BLOCKER_STATUSES`,
  `BLOCKER_REMEDIATION`, `BLOCKER_META_RULE`, `CANCEL_CONTROL_LABEL`, `CANCEL_CONTROL_TITLE`,
  `CANCEL_LABEL_FORBIDDEN`, `CANCEL_SCOPE_RULE`, `CLEAR_FINISHED_SEMANTICS`,
  `KEBAB_MENU_ORDER_SEMANTICS`, `KEBAB_AVAILABILITY`; rewrote `STATUS_PILL_TABLE`
  (`textClass` -> `labelClass` + `iconClass`), `PILL_CLASS_RULE`, `CONTRAST_RULE`; deleted the seven
  debt keys; `RED_COUNT_41` 9 -> 10, `RED_COUNT_43` 13 -> 15
- `contrast-matrix.json` - regenerated: `label` 80/80 pass worst 6.61, `icon` advisory (12 below 3.0,
  worst 1.94)
- `implementation-plan.md` - AC-40.6, AC-41.4, AC-41.8, **new AC-41.10**, AC-42.2, AC-42.3, AC-42.4,
  AC-42.5, AC-43.8, **new AC-43.14 / AC-43.15**, four Spec Sufficiency rows, the pill-foreground
  source row, and the `status-tokens.ts` Files-Modified row
- `task.md` - rows 3 and 8 (the known-issue creation step is deleted; there is no debt to track)
- `correction-census.json` - seven R5 values; driver unchanged since Round 3

**Verdict authorship unchanged:** this section is the corrections agent's record. It asserts no
verdict. Round 5's verdict is the external reviewer's alone.

---

## Round 5

### Intent Anchor

Executing this plan should produce foundations for a queue UI that keeps every useful operation
reachable, describes the real scope of actions, makes blocked jobs understandable and recoverable,
and stays readable in both themes. The palette and blocker-reset policy now meet that objective, but
four user-visible contradictions remain in the card contract, so the plan is not ready to execute.

### Findings

| Finding | Severity | Confidence | Wrong delivered behavior | Evidence | Recommendation |
|---|---|---|---|---|---|
| F1 | **High** | High | **A real `QualityBlocked` card cannot render the blocker reason AC-43.15 promises.** Both production paths that create the state leave `error_message=None`: enqueue assigns `QualityBlocked` and then constructs the job with no error, while `apply_lock()` transitions the job without adding one. A component test can pass with a synthetic error string, but a person whose job is blocked by SABR will not receive the required reason from the product. | `implementation-plan.md:421`; `named-sets.json:645`; `packages/core/src/avkit_core/services/download.py:228-243,351-365` | Give the reason a real producer on both `Pending -> QualityBlocked` paths (or derive it from a shared blocker-reason contract), and test the service/API payload that feeds the card rather than only a fabricated component prop. Keep remediation as the separate “what to change” copy. |
| F2 | **High** | High | **The corrected kebab test removes valid downward reorder actions from a common row.** `KEBAB_AVAILABILITY` says a non-last row offers `Move down` and `Move to bottom`, but AC-43.8 requires a first-row Pending job to show only `Copy path` and `Remove`. For a queue with more than one item, executing the AC literally makes the top Pending job impossible to move down from its row menu, silently losing two operations the proposal promises. | `implementation-plan.md:414`; `named-sets.json:657-665`; `docs/proposals/2026-08-27-queue-card-ui-proposal.md:78,156-159` | For a first-but-not-last Pending row with all callbacks supplied, require `Copy URL`, `Move down`, `Move to bottom`, and `Remove`. Use a one-row queue if the intended test case is “only Copy + Remove.” Keeping inapplicable actions absent is the right rule. |
| F3 | **High** | High | **The Cancel wording remedy now requires a confirmation dialog even though the product contract says queue-level Cancel is immediate.** AC-43.14's call chain clicks the card action and asserts confirm copy; the proposal's destructive-action ladder explicitly assigns Cancel no dialog because the job is re-queueable. This would add an unchosen friction step to a time-sensitive stop action and conflicts with the presentational `onCancelQueue` callback contract. | `implementation-plan.md:401,411,420`; `docs/proposals/2026-08-27-queue-card-ui-proposal.md:146-151` | Keep the exact `Cancel queue` accessible name and scope-bearing title, but assert that activation calls `onCancelQueue` directly and does not open a confirm. Reserve `ConfirmModal` for Remove/Clear actions. |
| F4 | **Medium** | High | **The menu can say “Copy path” while copying a URL.** The action is always available and falls back to the source URL before an output path exists, yet its only visible label is `Copy path`. On a Pending row, a person choosing it receives different clipboard content from what the command names. | `named-sets.json:270-278,657-665`; `docs/proposals/2026-08-27-queue-card-ui-proposal.md:78` | Make the visible label state-dependent (`Copy URL` until an output path exists, `Copy path` afterward) while keeping one canonical action id/order slot. Test both labels and clipboard values. |

### Round 4 Remedy Assessment

- **F1 palette: accepted.** Reading the human lock as Zorivest token values/hues rather than its
  same-token class combination is disclosed and defensible. `--color-fg` is byte-identical in both
  repos and the 10% status wash plus status icon preserves the hue; the label does not read as an
  unstyled grey chip. The measured label matrix is 80/80 at or above 4.5, worst 6.61. The redundant
  `aria-hidden` icon may remain advisory.
- **F2 re-queue: policy accepted, explanation path incomplete.** The service-level live-SABR check
  and 409 are correct: a 200 that immediately re-blocks would be less honest. MCP reaches the same
  HTTP reset route; the repository bulk `reset_failed()` queries only `Failed` rows; and
  `clear_sabr()` first makes SABR inactive before releasing `QualityBlocked` jobs. None bypasses the
  active-lock rule. F1 above is the remaining production-data hole.
- **F3 wording: label/title accepted; confirm requirement rejected.** The row-local control must say
  `Cancel queue`, but the action remains no-dialog.
- **F4 Clear finished: accepted.** Snapshot, continue-on-failure, preserved successes, no file
  deletion, one reconciliation fetch, and per-failure reporting form a complete deferred contract.
- **F5 applicability: absence is the right interaction.** Context menus should omit actions that
  cannot work; disabled rows would add keyboard stops without helping. F2 is a bad expected set, not
  a reason to abandon the absence rule.

### Scope and Residual Risk

MEU-40..43 still honestly stop at canon, re-queue widening, primitives, and unmounted card/list
components; page migration, bulk controls, Clear finished wiring, and Electron E2E remain named
later MEUs. The reduced control model retains all operations once F2/F4 are corrected.

The remaining non-blocking risk is copy drift between the Python 409 message and TypeScript card
remediation: `BLOCKER_REMEDIATION` is a plan contract, not a runtime cross-language module. Exact
tests against the same named value make the first delivery auditable, but later changes will still
need a contract test or generated shared source.

### Permitted Verification

- `assert-red-oracle.ps1 -SelfTest` -> `PASS: RED_ORACLE selftest 11 cases`
  (`C:/Temp/av-kit/r5-red-selftest.txt`).
- `assert-page-isolation.ps1 -SelfTest` -> `PASS: PAGE_ISOLATION selftest 19 cases`
  (`C:/Temp/av-kit/r5-iso-selftest.txt`).
- Read-only source/plan sweeps covered the requested plan artifacts, proposal/mockup, Zorivest
  palette, download domain/service transitions, API/MCP reset surfaces, and repository bulk reset.

No pytest, Vitest, npm test/build, Playwright, MEU-status command, OpenAPI export, issue-triage
command, product generator, or real-tree page-isolation capture was run.

### Verdict

`changes_required` - four Round 5 product findings. Correct F1-F4 above and return for the final
Round 6 review. The palette remedy, live-SABR 409 policy, Clear-finished contract, and omit-inapplicable
menu rule should be preserved.

---

## Round 6 Corrections - Reviewer R5-F1..F4 (corrections agent)

Round 5 returned `changes_required` with **four product findings and zero procedural findings**, and
explicitly ratified the four Round 4 remedies it did not fault: the palette reading, the live-SABR
409, the Clear-finished contract, and the omit-inapplicable menu rule. All four new findings are
accepted; **two of them are corrections to Round 5's own remedies**, which is the honest read - the
fixes introduced the wrongness, not the original plan.

| F | Sev | Wrong behaviour it named | Disposition |
|---|---|---|---|
| R5-F1 | High | A real `QualityBlocked` card cannot render the reason AC-43.15 promises - both producers leave `error_message=None` | **Accepted.** `BLOCKER_REASON_RULE` + new AC-41.11 give the reason a producer at the transition |
| R5-F2 | High | The R5 kebab expected set strips `Move down`/`Move to bottom` from the top row of every multi-item queue | **Accepted.** Availability is now explicitly **per action, never per group**; AC-43.8 gets a fourth case |
| R5-F3 | High | The R5 cancel remedy invented a confirm dialog against the Spec's own destructive-action ladder | **Accepted and withdrawn.** `CANCEL_CONFIRM_POLICY`; AC-43.14 now asserts **no** dialog |
| R5-F4 | Med | The menu can read `Copy path` while copying a URL | **Accepted.** `KEBAB_MENU_ORDER` becomes action **ids**; `KEBAB_ACTION_LABELS` makes the copy label state-dependent |

### R5-F1 - the reason had no producer

Verified in source before writing the fix, and the reviewer is exactly right:

- `services/download.py:228-247` - `enqueue` chooses `DownloadStatus.QualityBlocked` in one branch and
  then constructs the `DownloadJob` with `error_message=None` a few lines later.
- `services/download.py:351-365` - `apply_lock()` transitions `Pending -> QualityBlocked` via
  `job.transition(...)` and saves, adding nothing.
- `services/download.py:506-507` - `AgeRestricted`, by contrast, **already** conforms:
  `_finish(job.id, DownloadStatus.AgeRestricted, error=str(exc))`, with the text raised at
  `infrastructure/.../adapter.py:392,446`.

So the card copy `BLOCKER_META_RULE` requires simply did not exist in production data. AC-43.15 could
have passed forever against a fabricated prop while a blocked user saw an empty explanation. New
**AC-41.11** gives it a producer at both `QualityBlocked` transitions, rendered from
`BLOCKER_REASON_TEMPLATE`, and - per the reviewer - asserts it against the **persisted repository row
and the `GET /downloads` payload**, never a hand-built `DownloadJob`. `AgeRestricted` is asserted to
already conform and is not touched. AC-43.15 is sharpened so neither string may be authored by the
component, and so substituting remediation for a missing reason fails.

No existing test asserts `error_message is None` for a `QualityBlocked` job (`rg` over
`tests/unit/test_domain.py` and `tests/unit/test_services.py`: the four `QualityBlocked` sites assert
status only), so this adds behaviour without editing an existing assertion.

**Self-caught in the same pass, reported not hidden:** AC-41.10 and AC-41.11 both edit
`services/download.py`, but the MEU-41 Files-Modified block still carried the standing note *"Services
are unchanged in code."* That contradiction was mine, introduced in Round 5 when AC-41.10 landed
without a file-set update. The file is now listed, the note is narrowed to `services/conversion.py`
(which really is untouched) with an explicit containment clause, and task row 6's instruction, durable
outputs, and anti-placeholder path set all name it.

### R5-F2 - availability is per action, not per group

`KEBAB_AVAILABILITY` already said a non-last row offers `Move down` and `Move to bottom`, but Round
5's AC-43.8 expected set for a first-row Pending job listed only `Copy path` and `Remove`. Executed
literally, the top job of any multi-item queue would lose both downward reorder operations - the
proposal promises four moves (proposal:78, §8). The rule now states availability is evaluated **per
action, never per group**, and AC-43.8 carries four cases instead of three: mid-list `Done` (all
eight), **first-but-not-last `Pending`** (`copy-location`, `move-down`, `move-bottom`, `remove`),
**one-item queue** (`copy-location` + `remove` - the only case that legitimately drops all four
moves), and callback-starved (`remove` alone). The reviewer's judgement that absence beats disabled
is preserved unchanged.

### R5-F3 - the confirm dialog was a scope invention

proposal:146-149 puts it plainly: *"queue-level Cancel of a re-queueable job -> no dialog (re-queue is
cheap)"*, with `ConfirmModal` reserved for Remove and Clear. Round 5 bolted a confirm onto the cancel
**wording** fix, which is friction the human never chose on a time-sensitive stop, and it contradicted
the presentational `onCancelQueue` contract AC-43.5 asserts. Withdrawn. `CANCEL_CONFIRM_POLICY` records
the rule and the mistake; AC-43.14 now asserts activation calls `onCancelQueue` directly and that **no
`role="dialog"` appears**. The scope disclosure stays entirely in `CANCEL_CONTROL_LABEL` and
`CANCEL_CONTROL_TITLE` - which is what locking those two strings was for.

### R5-F4 - one action id, a label that tells the truth

`KEBAB_MENU_ORDER` is now a list of **action ids**; `KEBAB_ACTION_LABELS` maps id -> label, and
`copy-location` resolves to `Copy path` once an output path exists and `Copy URL` before then. One
canonical id, one order slot, honest copy. This is also the reading that reconciles the two Spec
sources, which had quietly disagreed: the proposal writes the action `Copy path/URL` (proposal:78) and
the mockup renders it `Copy URL` (mockup:287). AC-43.8 asserts label and clipboard payload
**together**, so the item can never name one thing and copy another.

### Census over the correction (PR-6)

Five `r6-` values added; the whole census re-run in all three directions.

```
Blast-radius census: 35 values changed, 216 literals swept (old+new+variant), 413 sites found.
  predicate 40|8|8|MATCH
  predicate 41|11|11|MATCH
  predicate 42|13|13|MATCH
  predicate 43|15|15|MATCH
PASS: CORRECTION_CENSUS   EXIT=0
```

`RED_COUNT_41` 10 -> **11** (AC-41.11). Transitive binding census:
`top-level keys: 190 | bound: 190 | UNBOUND: 0` / `DANGLING citations: 0`.

### Per-hit disposition log (R6 values, all three directions)

rg exit codes: 0 = matched, 1 = no match, >1 = real error. For an `old` literal rc=1 is the good
outcome; for a `new` literal rc=0 is.

| slug | dir | i | rc | hits | literal | disposition |
|---|---|---|---|---|---|---|
| `r6-blocker-reason` | new | 0 | 0 | 2 | `BLOCKER_REASON_RULE` | **updated** - the edit landed |
| `r6-blocker-reason` | new | 1 | 0 | 3 | `BLOCKER_REASON_TEMPLATE` | **updated** - the edit landed |
| `r6-blocker-reason` | new | 2 | 0 | 1 | `BLOCKER_REASON_PRODUCERS` | **updated** - the edit landed |
| `r6-blocker-reason` | new | 3 | 0 | 6 | `AC-41.11` | **updated** - the edit landed |
| `r6-blocker-reason` | variant | 0 | 0 | 6 | `error_message` | confirmed-consistent - present as required |
| `r6-blocker-reason` | variant | 1 | 0 | 1 | `never a hand-built `DownloadJob`` | confirmed-consistent - present as required |
| `r6-blocker-reason` | variant | 2 | 0 | 6 | `apply_lock` | confirmed-consistent - present as required |
| `r6-services-file-set` | old | 0 | 1 | 0 | `Services are unchanged in code` | **updated** - 0 stale sites remain |
| `r6-services-file-set` | new | 0 | 0 | 3 | `packages/core/src/avkit_core/services/download.py` | **updated** - the edit landed |
| `r6-services-file-set` | variant | 0 | 0 | 1 | `services/conversion.py` is unchanged in code` | confirmed-consistent - present as required |
| `r6-services-file-set` | variant | 1 | 0 | 1 | `no new module, no signature change` | confirmed-consistent - present as required |
| `r6-kebab-action-ids` | old | 0 | 1 | 0 | `"Open file",` | **updated** - 0 stale sites remain |
| `r6-kebab-action-ids` | old | 1 | 1 | 0 | `Copy path` and `Remove` | **updated** - 0 stale sites remain |
| `r6-kebab-action-ids` | new | 0 | 0 | 3 | `KEBAB_ACTION_LABELS` | **updated** - the edit landed |
| `r6-kebab-action-ids` | new | 1 | 0 | 2 | `copy-location` | **updated** - the edit landed |
| `r6-kebab-action-ids` | new | 2 | 0 | 1 | `move-bottom` | **updated** - the edit landed |
| `r6-kebab-action-ids` | variant | 0 | 0 | 1 | `per action, never per group` | confirmed-consistent - present as required |
| `r6-kebab-action-ids` | variant | 1 | 0 | 2 | `Copy URL` | confirmed-consistent - present as required |
| `r6-kebab-action-ids` | variant | 2 | 0 | 1 | `one-item queue` | confirmed-consistent - present as required |
| `r6-kebab-action-ids` | variant | 3 | 0 | 5 | `KEBAB_MENU_ORDER` | confirmed-consistent - present as required |
| `r6-cancel-no-confirm` | old | 0 | 1 | 0 | `the same scope wording appears in whatever confirm step` | **updated** - 0 stale sites remain |
| `r6-cancel-no-confirm` | new | 0 | 0 | 2 | `CANCEL_CONFIRM_POLICY` | **updated** - the edit landed |
| `r6-cancel-no-confirm` | variant | 0 | 0 | 1 | `no** confirmation dialog` | confirmed-consistent - present as required |
| `r6-cancel-no-confirm` | variant | 1 | 0 | 1 | `re-queue is cheap` | confirmed-consistent - present as required |
| `r6-cancel-no-confirm` | variant | 2 | 0 | 3 | `CANCEL_CONTROL_LABEL` | confirmed-consistent - present as required |
| `r6-red-counts` | old | 0 | 1 | 0 | `"RED_COUNT_41": 10` | **updated** - 0 stale sites remain |
| `r6-red-counts` | new | 0 | 1 | 0 | `"RED_COUNT_41": 11` | **absent by design** - the value is stated once in `named-sets.json`, outside the swept scope |

**R6 totals: 27 literals swept, 52 sites found, every row dispositioned.**
Untruncated receipts: `C:/Temp/av-kit/census/census-r6-*.txt`; index at
`C:/Temp/av-kit/census/INDEX.txt`.

### Files changed this round

- `named-sets.json` - added `BLOCKER_REASON_TEMPLATE`, `BLOCKER_REASON_RULE`,
  `BLOCKER_REASON_PRODUCERS`, `KEBAB_ACTION_LABELS`, `CANCEL_CONFIRM_POLICY`; rewrote
  `KEBAB_MENU_ORDER` (labels -> action ids), `KEBAB_AVAILABILITY` (re-keyed on ids),
  `KEBAB_MENU_ORDER_SEMANTICS`, `CANCEL_SCOPE_RULE`; `RED_COUNT_41` 10 -> 11
- `implementation-plan.md` - **new AC-41.11**, AC-43.8 (rewritten), AC-43.14 (confirm withdrawn),
  AC-43.15 (sharpened), three Spec Sufficiency rows, the MEU-41 Files-Modified block and its standing
  note, the MEU-43 `QueueCardMenu.tsx` row
- `task.md` - row 6 (service edits, durable outputs, anti-placeholder paths)
- `correction-census.json` - five R6 values; driver unchanged since Round 3

**Round 6 is the last configured round** (`PLAN_REVIEW_MAX_ROUND` = 6). A Round 6
`changes_required` is a HARD STOP requiring the human.

**Verdict authorship unchanged:** this section is the corrections agent's record. It asserts no
verdict. Round 6's verdict is the external reviewer's alone.

---

## Round 6

### Intent Anchor

Executing this plan should produce queue-card foundations that preserve every useful action, explain
blocked jobs from real persisted data, expose the true scope of destructive controls, and remain
operable by keyboard and assistive technology. The Round 5 corrections repair all four reported
contradictions, but two product-level holes remain: the new blocker reason becomes stale over an
existing job mutation, and the clickable-card contract can still contain nested action controls.

### Findings

| Finding | Severity | Confidence | Wrong delivered behavior | Evidence | Recommendation |
|---|---|---|---|---|---|
| R6-F1 | **High** | High | **The new `QualityBlocked` reason is not maintained over the real job lifecycle.** AC-41.11 covers the two paths that first enter `QualityBlocked`, but the existing Apply Defaults path also rewrites `quality`, `audio_format`, and `audio_only` on an already-`QualityBlocked` row without refreshing `error_message`; a later `apply_lock()` pass deliberately leaves an already-blocked row untouched. A user can therefore change Downloader defaults and see the card's current quality disagree with its old quality-specific reason, while a pre-R6 persisted blocked row can remain reasonless forever. `GET /downloads` faithfully serializes that stale/empty field, so AC-43.15 cannot repair it in the component. The prescribed sentence also exposes the internal acronym “SABR” without explaining it, despite calling itself human-readable. | `implementation-plan.md:289-290,427`; `named-sets.json:667-673`; `packages/core/src/avkit_core/services/download.py:351-388`; `packages/api/src/avkit_api/routes/downloads.py:40-56` | Make the invariant cover every persisted `QualityBlocked` row and every mutation of the fields used by its reason. Either use plain-language, quality-independent reason copy or recompute/backfill the reason in Apply Defaults and the already-blocked `apply_lock()` path. Add repository + `GET /downloads` cases for a legacy row and for Apply Defaults changing a blocked job's quality. |
| R6-F2 | **High** | High | **The plan can ship Retry/Cancel/Open and the kebab nested inside the card's `role="button"` region while every AC passes.** AC-43.2 proves only that the selection checkbox is outside the clickable region. The proposal assigns the card body `role="button"`, and its mockup places the primary and kebab buttons inside that body; the plan's general note that interactive controls must not nest has no corresponding observable for those two zones. A keyboard or screen-reader user can therefore activate Retry or the menu and also trigger card-open through bubbling, or lose the descendant controls' independent semantics/focus. | `implementation-plan.md:413-420,443`; `docs/proposals/2026-08-27-queue-card-ui-proposal.md:69-87`; `docs/proposals/2026-08-27-queue-card-ui-mockup.html:261-277,284-287` | Require the selection checkbox, primary-action control, and kebab/menu trigger to be siblings of—not descendants of—the `role="button"` region. Test the ancestry and independent keyboard/click behavior for all three interactive zones, including that activating an action never invokes `onOpen`. |

No Critical findings were identified. Both findings describe user-visible failures and are independent
of artifact formatting, receipt mechanics, or workflow ceremony.

### Round 5 Remedy Assessment

- **R5-F1: accepted but lifecycle-incomplete.** The enqueue and `Pending -> QualityBlocked`
  producers now have a real persisted/API assertion. R6-F1 is a new failure introduced by making
  the reason quality-specific without covering the existing mutation of that quality or old rows.
- **R5-F2: accepted.** Per-action availability and all four AC-43.8 cases are correct. A
  first-but-not-last row retains both downward moves; only a one-item queue loses all four moves.
- **R5-F3: accepted.** `Cancel queue` accurately discloses scope and invokes `onCancelQueue`
  directly with no invented dialog.
- **R5-F4: accepted.** The state-dependent `Copy path` / `Copy URL` label is more honest, not more
  confusing, because the label and clipboard payload change together. A failed job with no recorded
  output path correctly offers the source URL; a recorded output path is named as a path.

### Scope and Residual Risk

MEU-40..43 still stop honestly at canon, backend widening, primitives, and unmounted card/list
components. Page migration, bulk actions, Clear finished wiring, drag reorder, and Electron E2E stay
in their named later MEUs; no silent scope loss was found in those boundaries. The USER_LOCKS,
reduced control model, re-queue widening, cancel behavior, and measured pill palette otherwise remain
coherent.

The Round 5 cross-language drift risk is acceptable for this MEU set. The blocker *reason* is not a
second TypeScript constant: Python writes it into the job and the card consumes that payload. The
remediation sentence is duplicated across the Python 409 and TypeScript card surfaces, but both are
contract-tested against the same named value. A generated runtime source would reduce later
maintenance risk, but it is not required before execution.

### Verification Performed

- Read the plan, task, named sets, proposal, mockup, Round 5 findings, and Round 6 corrections.
- Traced `QualityBlocked` through `enqueue`, `apply_lock`, `apply_defaults_to_pending`, the domain
  transition, repository-facing service operations, `_job_out`, and `DownloadJobOut`.
- Checked AC-43.8's four action sets against each per-action availability condition and checked the
  state-dependent copy label against its payload rule.
- Did not run the optional hermetic oracles because they do not adjudicate either product finding.
  No pytest, Vitest, npm test/build, Playwright, MEU-status command, OpenAPI export, issue-triage
  command, product generator, or real-tree page-isolation capture was run.

### Verdict

`changes_required` — two Round 6 High product findings. The plan can deliver stale or missing blocker
explanations after a normal settings action, and it can deliver nested card controls that are not
independently operable. Because Round 6 is the configured maximum, this verdict is the required HARD
STOP: return the plan to the human for direction. It does not authorize another correction cycle or
execution.

---

## Round 7 Corrections - Reviewer R6-F1..F2 (corrections agent)

Round 6 returned `changes_required` at the configured cap, which was a HARD STOP. The human read the
verdict and authorised **one more round**; that authorisation is what lifts the stop, and
`PLAN_REVIEW_MAX_ROUND` is 7 for this plan. Both findings are High, both are accepted, and neither is
argued down.

Round 6 also assessed all four Round 5 remedies **accepted** - per-action kebab availability, the
withdrawn cancel dialog, and the state-dependent copy label are closed and not reopened here. The
Round 5 cross-language drift risk was explicitly downgraded to acceptable for this MEU set, on the
reasoning that the reason is job data rather than a second TypeScript constant.

| F | Sev | Wrong behaviour it named | Disposition |
|---|---|---|---|
| R6-F1 | High | The new `QualityBlocked` reason is not maintained over the job lifecycle - Apply Defaults rewrites the quality it names, `apply_lock` never backfills a legacy row, and the copy leaks "SABR" | **Accepted.** Copy becomes quality-independent and acronym-free; presence becomes an invariant (AC-41.12), not a per-site patch |
| R6-F2 | High | Retry, Cancel/Open and the kebab can ship nested inside the card's `role="button"` while every AC passes - AC-43.2 proves only the checkbox | **Accepted.** `CLICKABLE_REGION_RULE` + new AC-43.16 assert ancestry and independent operation for all three zones |

### R6-F1 - the interpolation was the bug, so it is gone rather than maintained

The reviewer offered two remedies: quality-independent copy, **or** recompute/backfill at every
mutation. Taking the first, because the second leaves the failure mode alive and merely adds sites
that must remember to run. Verified in source first:

- `services/download.py:369-391` - `apply_defaults_to_pending` matches
  `{Pending, QualityBlocked}` and saves a row with new `quality`/`audio_format`/`audio_only` and the
  **old `error_message` copied verbatim** through `**job.__dict__`. Exactly the drift described.
- `services/download.py:351-365` - `apply_lock` matches an already-`QualityBlocked` incompatible row,
  passes both `continue` guards, and then does nothing: the `if job.status is Pending` branch is the
  only write. A row blocked before this MEU ships is never revisited, so it stays reasonless forever.
- `DownloadJobOut` / `_job_out` serialize `error_message` faithfully - the reviewer is right that the
  API cannot repair this and the card must not.

`BLOCKER_REASON_TEMPLATE['QualityBlocked']` is now *"YouTube is limiting which formats this video will
serve right now, so the requested quality or audio format is not available."* - no `{quality}`
placeholder, no acronym, and it covers the audio-only branch of `_incompatible()` as well as the
video branch. `BLOCKER_REMEDIATION['QualityBlocked']` loses "SABR" for the same reason; that string is
also the 409 body AC-41.10 asserts, so both surfaces move together. `BLOCKER_REASON_COPY_RULE` records
why the interpolation is forbidden rather than merely absent, and AC-41.11's negative oracle fails the
plan if a placeholder or the acronym returns.

With nothing interpolated, "keep the reason true" collapses into "keep the reason present", which is
what `BLOCKER_REASON_INVARIANT` states as a **persisted-state invariant** rather than a callsite list:
every persisted `QualityBlocked` row carries the reason; no row persisted out of a blocker state
retains one. `BLOCKER_REASON_PRODUCERS` is restructured into three phases - `enters`,
`persists-while-blocked`, `leaves` - so the sites are enumerable rather than remembered. New
**AC-41.12** asserts clause (1) against the two mutations the reviewer named, both seeded as *persisted
state* rather than fresh enqueues: a legacy `error_message=None` row backfilled by `apply_lock`, and a
blocked row put through Apply Defaults.

**Self-caught while verifying this, and reported rather than folded in silently:** clause (2) did not
exist, and it needed to. `DownloadJob.transition` is `replace(self, status=...)`
(`domain/download.py:111-119`) and preserves `error_message`, so `clear_sabr` - which moves every
`QualityBlocked` job back to `Pending` - would have handed each one back to the queue still displaying
the sentence explaining why it was blocked. Before Round 6 that was invisible, because the reason did
not exist; Round 6's fix is what created the leak. New **AC-41.13** clears it at the transition. The
domain's `reset_failed` already sets `error_message=None` (`domain/download.py:121-128`) and is
asserted, not changed - AC-41.10's widened re-queue inherits that.

### R6-F2 - the first finding in seven rounds that is not a remedy defect

Confirmed against the mockup: `mockup:261-277` puts `<button class="iconbtn">` (the primary action)
and `<button class="iconbtn ghost">` (the kebab) **inside** `<div class="body">`, and proposal §4 is
what gives that body `role="button"`. Only the checkbox is already a sibling - and only the checkbox
had an AC proving it. So the reviewer's charge is exact: every AC could pass on a card that nests two
interactive controls in a button.

`CLICKABLE_REGION_RULE` + `CARD_INTERACTIVE_ZONES` now require all three zones to be siblings of the
open-region, and **AC-43.16** asserts ancestry directly plus independent operation - each control is
its own tab stop, click and keyboard each invoke its own callback exactly once, and `onOpen` is not
called. AC-43.2 gains a pointer to it so its partial proof is not mistaken for a whole one.

Worth stating plainly: this changes the DOM, not the design. The mockup's own zone strip
(`mockup:278`) already lays out `action` and the kebab as separate right-edge columns, so hoisting them
out of the open-region is layout-neutral - which is also why the nesting slipped through unnoticed.
The standards basis is the axe `nested-interactive` rule, WCAG 2.2 SC 4.1.2, and the HTML spec's
prohibition on interactive content inside `button`.

### Census over the correction (PR-6)

Five `r7-` values added; the whole census re-run in all three directions.

```
Blast-radius census: 40 values changed, 245 literals swept (old+new+variant), 483 sites found.
  predicate 40|8|8|MATCH
  predicate 41|13|13|MATCH
  predicate 42|13|13|MATCH
  predicate 43|16|16|MATCH
PASS: CORRECTION_CENSUS   EXIT=0
```

`RED_COUNT_41` 11 -> **13** (AC-41.12, AC-41.13); `RED_COUNT_43` 15 -> **16** (AC-43.16). Transitive
binding census: `top-level keys: 194 | bound: 194 | UNBOUND: 0` / `DANGLING citations: 0`.

The binding census caught one defect in this round's own prose: AC-41.11's new negative oracle wrote
the acronym as `` `SABR` ``, a backticked all-caps token that resolves to no named-set key. Fixed by
unbackticking it rather than by adding the word to the checker's exemption list - loosening the
checker to accommodate my prose would defeat the check.

### Per-hit disposition log (R7 values, all three directions)

rg exit codes: 0 = matched, 1 = no match, >1 = real error. For an `old` literal rc=1 is the good
outcome; for a `new` literal rc=0 is.

| slug | dir | i | rc | hits | literal | disposition |
|---|---|---|---|---|---|---|
| `r7-reason-copy` | old | 0 | 1 | 0 | `formatted with that job's `quality`` | **updated** - 0 stale sites remain |
| `r7-reason-copy` | old | 1 | 1 | 0 | `SABR restrictions are active for this video` | **updated** - 0 stale sites remain |
| `r7-reason-copy` | new | 0 | 0 | 2 | `BLOCKER_REASON_COPY_RULE` | **updated** - the edit landed |
| `r7-reason-copy` | new | 1 | 0 | 1 | `quality-independent` | **updated** - the edit landed |
| `r7-reason-copy` | variant | 0 | 0 | 1 | `**verbatim**` | confirmed-consistent - present as required |
| `r7-reason-copy` | variant | 1 | 1 | 0 | `YouTube is limiting which formats` | confirmed-consistent - **absent on purpose**: the reason text is stated once in `BLOCKER_REASON_TEMPLATE` and the plan cites the key, never the string (PR-9) |
| `r7-reason-copy` | variant | 2 | 0 | 1 | `regains a `{quality}`-style placeholder` | confirmed-consistent - present as required |
| `r7-reason-invariant` | new | 0 | 0 | 6 | `BLOCKER_REASON_INVARIANT` | **updated** - the edit landed |
| `r7-reason-invariant` | new | 1 | 0 | 4 | `AC-41.12` | **updated** - the edit landed |
| `r7-reason-invariant` | new | 2 | 0 | 1 | `persists-while-blocked` | **updated** - the edit landed |
| `r7-reason-invariant` | variant | 0 | 0 | 6 | `apply_defaults_to_pending` | confirmed-consistent - present as required |
| `r7-reason-invariant` | variant | 1 | 0 | 1 | `legacy row` | confirmed-consistent - present as required |
| `r7-reason-invariant` | variant | 2 | 0 | 2 | `falls through with no write` | confirmed-consistent - present as required |
| `r7-reason-invariant` | variant | 3 | 0 | 4 | `BLOCKER_REASON_PRODUCERS` | confirmed-consistent - present as required |
| `r7-reason-exit-edge` | new | 0 | 0 | 4 | `AC-41.13` | **updated** - the edit landed |
| `r7-reason-exit-edge` | new | 1 | 0 | 5 | `clear_sabr` | **updated** - the edit landed |
| `r7-reason-exit-edge` | variant | 0 | 0 | 2 | `replace(self, status=...)` | confirmed-consistent - present as required |
| `r7-reason-exit-edge` | variant | 1 | 0 | 1 | `reset_failed` is asserted to **already** conform` | confirmed-consistent - present as required |
| `r7-nested-interactive` | new | 0 | 0 | 3 | `CLICKABLE_REGION_RULE` | **updated** - the edit landed |
| `r7-nested-interactive` | new | 1 | 0 | 2 | `CARD_INTERACTIVE_ZONES` | **updated** - the edit landed |
| `r7-nested-interactive` | new | 2 | 0 | 4 | `AC-43.16` | **updated** - the edit landed |
| `r7-nested-interactive` | variant | 0 | 0 | 1 | `nested-interactive` | confirmed-consistent - present as required |
| `r7-nested-interactive` | variant | 1 | 0 | 2 | `kebab-trigger` | confirmed-consistent - present as required |
| `r7-nested-interactive` | variant | 2 | 0 | 1 | `layout-neutral` | confirmed-consistent - present as required |
| `r7-nested-interactive` | variant | 3 | 0 | 1 | `AC-43.16 extends this ancestry proof` | confirmed-consistent - present as required |
| `r7-red-counts` | old | 0 | 1 | 0 | `"RED_COUNT_41": 11` | **updated** - 0 stale sites remain |
| `r7-red-counts` | old | 1 | 1 | 0 | `"RED_COUNT_43": 15` | **updated** - 0 stale sites remain |
| `r7-red-counts` | new | 0 | 1 | 0 | `"RED_COUNT_41": 13` | **absent by design** - the value is stated once in `named-sets.json`, outside the swept scope |
| `r7-red-counts` | new | 1 | 1 | 0 | `"RED_COUNT_43": 16` | **absent by design** - the value is stated once in `named-sets.json`, outside the swept scope |

**R7 totals: 29 literals swept, 55 sites found, every row dispositioned.**
Untruncated receipts: `C:/Temp/av-kit/census/census-r7-*.txt`; index at
`C:/Temp/av-kit/census/INDEX.txt`.

### Files changed this round

- `named-sets.json` - added `BLOCKER_REASON_COPY_RULE`, `BLOCKER_REASON_INVARIANT`,
  `CARD_INTERACTIVE_ZONES`, `CLICKABLE_REGION_RULE`; rewrote `BLOCKER_REASON_TEMPLATE`
  (quality-independent, acronym-free), `BLOCKER_REMEDIATION['QualityBlocked']`,
  `BLOCKER_REASON_RULE`, `BLOCKER_REASON_PRODUCERS` (three-phase); `RED_COUNT_41` 11 -> 13,
  `RED_COUNT_43` 15 -> 16
- `implementation-plan.md` - **new AC-41.12, AC-41.13, AC-43.16**; AC-41.11 (verbatim template, new
  negative oracle) and AC-43.2 (cross-reference) amended; three Spec Sufficiency rows; the MEU-41
  Files-Modified row and its containment note
- `task.md` - row 6 (the invariant across all its sites) and the MEU-43 Green row (sibling rendering)
- `correction-census.json` - five R7 values; driver unchanged since Round 3

**Verdict authorship unchanged:** this section is the corrections agent's record. It asserts no
verdict. Round 7's verdict is the external reviewer's alone.

---

## Round 7

### Intent Anchor

Executing this plan should produce queue-card foundations that preserve useful queue actions,
explain blocked jobs from honest persisted data, and give pointer, keyboard, and assistive-technology
users independent controls in a predictable order. The quality-independent copy and the revised card
DOM are the right product choices, but the persisted-state invariant still has one lifecycle hole
that leaves an upgraded user's existing blocked row unexplained.

### Findings

| Finding | Severity | Confidence | Wrong delivered behavior | Evidence | Recommendation |
|---|---|---|---|---|---|
| R7-F1 | **High** | High | **A pre-existing `QualityBlocked` row can still reach the card with no reason, including immediately after the user clicks Retry and the retry is refused.** `BLOCKER_REASON_INVARIANT` promises that every persisted blocked row is populated, including rows created before this release, but AC-41.12 repairs only rows that happen to pass through `apply_lock()` while still incompatible or Apply Defaults. There is no migration, startup sweep, read normalization, or persistence-boundary guard. A user who upgrades and simply opens the queue therefore still receives `error_message=null`; if they click Retry while the restriction remains active, AC-41.10 explicitly requires the job to stay blocked with “nothing written,” so the blank card survives the most relevant user action. Reordering also updates only `queue_position` and preserves the invalid row. The card cannot repair this without masking the backend defect. | `implementation-plan.md:289,291,318`; `named-sets.json:672-685,713`; `task.md:49`; `packages/core/src/avkit_core/services/download.py:295-310`; `packages/infrastructure/src/avkit_infra/database/repositories.py:85-96`; `packages/infrastructure/src/avkit_infra/database/migrations.py:11-73` | Treat this as a real persisted-data invariant: add an idempotent migration/backfill for existing `QualityBlocked` rows before they can be listed, centralize future `DownloadJob` add/save validation or normalization at the domain/persistence boundary, and make the still-incompatible Retry path canonicalize a legacy row before returning 409. Add a reopened-SQLite/API case that performs no `apply_lock` or Apply Defaults call, plus a legacy-row Retry-refusal case. Once legacy data is normalized, `reorder_queue` is harmless because it changes only position; Remove/delete paths need no repair because no row survives. |

No Critical findings were identified. R7-F1 is a delivered-product failure, not a process or
artifact-compliance objection.

### Round 6 Remedy Assessment

- **R6-F1: copy accepted; persisted lifecycle still incomplete.** The quality-independent,
  acronym-free sentence is the right call. It says what happened without embedding mutable state,
  and `BLOCKER_REMEDIATION['QualityBlocked']` tells the person exactly where to go and what kind of
  setting to change. Naming the exact quality in the stored sentence is not worth restoring. The
  remaining defect is not the sentence; it is that the plan does not make the sentence exist for
  every row it claims to cover.
- **R6-F2: accepted and closed.** AC-43.16 requires checkbox, primary action, and kebab trigger to be
  siblings of the open-region, gives each its own tab stop, exercises pointer and keyboard
  activation, and proves `onOpen` is not called. Together with `QUEUE_CARD_ZONE_ORDER`, the natural
  tab sequence is checkbox -> open-region -> primary action -> kebab, matching the visual order.
  The non-interactive title/meta/progress/pill content remains the open-region's coherent body; no
  product-significant ambiguity warrants holding the plan.

### Lifecycle Walk

- `enqueue` and `Pending -> QualityBlocked` in `apply_lock` are correctly covered by AC-41.11.
- Apply Defaults and the incompatible already-blocked `apply_lock` branch are correctly covered by
  AC-41.12, but they are optional user/service actions rather than an upgrade-time repair.
- `clear_sabr` and domain `reset_failed` correctly clear the reason on the two live exit paths;
  AC-41.13 closes the exit edge.
- `reorder_queue` performs a repository-level position update only. It cannot create a bad
  status/reason pair, but it perpetuates an already-invalid legacy row, which is why the initial
  migration is required.
- `remove_from_queue` / `delete_all` leave no persisted row. `_finish` enters `AgeRestricted` from
  `Downloading` with `str(exc)` and otherwise leaves non-blocker states. Repository bulk
  `reset_failed()` selects only `Failed`. None is an additional blocker after the central invariant
  and legacy backfill exist.

### Scope and Residual Risk

No other silent scope loss was found across MEU-40..43. The USER_LOCKS, reduced action model,
re-queue widening, queue-level Cancel disclosure, state-dependent Copy path/URL label, and pill
palette remain coherent. The card components are intentionally unmounted in this session; real
Electron hit-target geometry and page-level focus restoration remain later migration/E2E risks, not
defects in these foundations.

The open-region contract is sufficient for this MEU: AC-43.1 fixes document order, AC-43.2 gives the
non-interactive body button semantics, and AC-43.16 isolates all three action controls. An explicit
browser assertion of the eventual visual hit rectangle is still useful when MEU-44 mounts the card,
but it is not a Round 7 finding.

### Verification Performed

- Read the implementation plan, task, named sets, proposal section 4, mockup card anatomy, Round 6
  findings, and the Round 7 corrections.
- Traced every production download write path through `DownloadService`, `DownloadJob.transition` /
  `reset_failed`, the SQLAlchemy repository, row mappers, and the append-only migration mechanism.
- Checked `enqueue`, `apply_lock`, Apply Defaults, `clear_sabr`, Retry, reorder, remove/delete,
  `_run_one` / `_finish`, worker completion/cancel paths, and repository bulk `reset_failed`.
- Did not run the optional hermetic oracles because neither adjudicates the persisted-data gap. No
  pytest, Vitest, npm test/build, Playwright, MEU-status command, OpenAPI export, issue-triage command,
  product generator, or real-tree page-isolation capture was run.

### Verdict

`changes_required` — one Round 7 High product finding. The copy and card interaction remedy should
be kept, but the plan still cannot deliver its own promise that every persisted blocker row—including
one present at upgrade—has an explanation. This final-round verdict returns the plan to the human and
does not authorize execution or another automatic correction cycle.

---

## Round 8 Corrections - Reviewer R7-F1 (corrections agent)

**No Round 8 review was dispatched.** The human read the Round 7 verdict and answered: *"fix the
finding and proceed to execution with human approved."* That is a direct chat message from the user
(`USER_EXPLICIT`), which under `plan_to_exec_gate == human` authorises the plan -> execution
transition on its own (GUARDRAILS SIGN 3(a)). This section is the record of the fix applied before
that transition, not a review.

Round 7 also closed R6-F2 (`accepted and closed`) and accepted the quality-independent copy. The one
open finding:

| F | Sev | Wrong behaviour it named | Disposition |
|---|---|---|---|
| R7-F1 | High | A pre-existing `QualityBlocked` row still reaches the card with no reason - including right after a refused Retry - because the invariant was enforced only in `apply_lock` and Apply Defaults, which an upgrading user may never trigger | **Accepted.** Enforcement moves to the persistence boundary, plus an idempotent upgrade backfill and canonicalization on the 409 path |

### The finding was mine, and precisely diagnosed

Round 7 wrote `BLOCKER_REASON_INVARIANT` as a promise over *persisted state* - explicitly including
rows blocked before the MEU ships - and then enforced it at two *optional service paths*. A user who
upgrades and simply opens the queue calls neither. The reviewer found the sharpest version of it:
AC-41.10 requires a still-incompatible Retry to stay blocked with nothing written, so the blank card
survives the one action a confused user actually takes. An invariant over persisted state has to be
enforced where state is persisted; anything else is a promise with no enforcer.

### The remedy - the reviewer's own first option, which shrinks the diff

`BLOCKER_REASON_ENFORCEMENT` names three mechanisms:

1. **boundary-normalizer.** `domain/download.py` gains `BLOCKER_REASONS` (the code-side home of the
   reason text) and a pure `normalize_blocker_reason(job)`. `SqlAlchemyDownloadRepository.add` and
   `.save` apply it. Verified those are the *only* two writers into `download_jobs`: `reorder` sets
   `queue_position`, `delete`/`delete_all` remove rows, and the bulk `reset_failed()` selects
   `Failed` only. **AC-41.14** asserts it at the repository with no service in the test.
2. **upgrade-backfill.** One idempotent `UPDATE` appended to `MIGRATIONS`, whose WHERE clause is
   `BLOCKER_REASON_MIGRATION_PREDICATE` and whose literal is built from `BLOCKER_REASONS` at import.
   `apply_migrations()` runs at engine init, before any route can list a job. **AC-41.15** seeds a
   pre-release database, opens a fresh engine, and asserts `GET /downloads` carries the reason with
   **no service call of any kind** - that absence is the AC's whole point, because it is the path the
   upgrading user actually takes - then re-runs the migration to prove idempotency.
3. **refusal-canonicalization.** The still-incompatible Retry path saves through the normalizing
   boundary before raising the 409, instead of writing nothing. New case **(c)** in AC-41.12.

Worth stating plainly: this makes the service diff **smaller**, not larger. Round 7's four
per-callsite reason writes in `services/download.py` - `enqueue`, `apply_lock` (both branches),
`apply_defaults_to_pending`, `clear_sabr` - are **deleted**. They all flow through `add`/`save`, so
the boundary covers them, and duplicating the logic at each site is exactly the fragility the finding
named. `services/download.py` keeps one edit: the AC-41.10 re-queue branch, now saving before it
raises. AC-41.11 is amended to say it proves the *outcome* at the two entry paths while AC-41.14
proves the *mechanism*.

**Self-derived, not in the finding:** moving the clear to the boundary means clause (2) now runs on
**every** save, not just `clear_sabr`. An unconditional "non-blocker status implies no message" would
have silently erased a `Failed` job's traceback. So the clear fires only when the message is
**exactly** one of the `BLOCKER_REASONS` values, and AC-41.14 asserts the `Failed`-traceback case
explicitly.

### Census over the correction (PR-6)

```
Blast-radius census: 45 values changed, 269 literals swept (old+new+variant), 522 sites found.
  predicate 40|8|8|MATCH
  predicate 41|15|15|MATCH
  predicate 42|13|13|MATCH
  predicate 43|16|16|MATCH
PASS: CORRECTION_CENSUS   EXIT=0
```

`RED_COUNT_41` 13 -> **15** (AC-41.14, AC-41.15). Transitive binding census:
`top-level keys: 196 | bound: 196 | UNBOUND: 0` / `DANGLING citations: 0`.

The binding census again caught this round's own prose: `` `UPDATE` `` (a SQL keyword, not a
contract) was unbackticked in both files. `BLOCKER_REASONS` and `MIGRATIONS` were added to the
checker's `CODE_SYMBOLS` allowlist, which is what that list is for - both are real production
symbols, not named-set keys.

### Per-hit disposition log (R8 values, all three directions)

| slug | dir | i | rc | hits | literal | disposition |
|---|---|---|---|---|---|---|
| `r8-boundary-enforcement` | old | 0 | 1 | 0 | `All four edits are `BLOCKER_REASON_INVARIANT` in one file` | **updated** - 0 stale sites remain |
| `r8-boundary-enforcement` | new | 0 | 0 | 5 | `BLOCKER_REASON_ENFORCEMENT` | **updated** - the edit landed |
| `r8-boundary-enforcement` | new | 1 | 0 | 4 | `normalize_blocker_reason` | **updated** - the edit landed |
| `r8-boundary-enforcement` | new | 2 | 0 | 6 | `AC-41.14` | **updated** - the edit landed |
| `r8-boundary-enforcement` | variant | 0 | 0 | 2 | `boundary-normalizer` | confirmed-consistent - present as required |
| `r8-boundary-enforcement` | variant | 1 | 0 | 9 | `repositories.py` | confirmed-consistent - present as required |
| `r8-boundary-enforcement` | variant | 2 | 0 | 6 | `BLOCKER_REASONS` | confirmed-consistent - present as required |
| `r8-boundary-enforcement` | variant | 3 | 0 | 1 | `**No reason-writing code**` | confirmed-consistent - present as required |
| `r8-upgrade-backfill` | new | 0 | 0 | 3 | `AC-41.15` | **updated** - the edit landed |
| `r8-upgrade-backfill` | new | 1 | 0 | 2 | `BLOCKER_REASON_MIGRATION_PREDICATE` | **updated** - the edit landed |
| `r8-upgrade-backfill` | new | 2 | 0 | 1 | `upgrade-backfill` | **updated** - the edit landed |
| `r8-upgrade-backfill` | variant | 0 | 0 | 1 | `apply_migrations` | confirmed-consistent - present as required |
| `r8-upgrade-backfill` | variant | 1 | 0 | 1 | `no service call of any kind` | confirmed-consistent - present as required |
| `r8-upgrade-backfill` | variant | 2 | 0 | 5 | `migrations.py` | confirmed-consistent - present as required |
| `r8-upgrade-backfill` | variant | 3 | 0 | 4 | `idempotent` | confirmed-consistent - present as required |
| `r8-refusal-canonicalization` | new | 0 | 0 | 1 | `refusal-canonicalization` | **updated** - the edit landed |
| `r8-refusal-canonicalization` | new | 1 | 0 | 2 | `AC-41.12c` | **updated** - the edit landed |
| `r8-refusal-canonicalization` | variant | 0 | 0 | 1 | `the 409 path writes nothing and leaves the row blank` | confirmed-consistent - present as required |
| `r8-refusal-canonicalization` | variant | 1 | 0 | 1 | `**(c) the refused Retry**` | confirmed-consistent - present as required |
| `r8-clear-narrowness` | new | 0 | 0 | 1 | `preserved untouched` | **updated** - the edit landed |
| `r8-clear-narrowness` | variant | 0 | 1 | 0 | `erase a Failed` | confirmed-consistent - absent as required |
| `r8-clear-narrowness` | variant | 1 | 0 | 1 | `exactly one of the `BLOCKER_REASONS` values` | confirmed-consistent - present as required |
| `r8-red-counts` | old | 0 | 1 | 0 | `"RED_COUNT_41": 13` | **updated** - 0 stale sites remain |
| `r8-red-counts` | new | 0 | 1 | 0 | `"RED_COUNT_41": 15` | **absent by design** - the value is stated once in `named-sets.json`, outside the swept scope |

**R8 totals: 24 literals swept, 57 sites found, every row dispositioned.**

### Files changed this round

- `named-sets.json` - added `BLOCKER_REASON_ENFORCEMENT`, `BLOCKER_REASON_MIGRATION_PREDICATE`;
  rewrote `BLOCKER_REASON_INVARIANT` (enforcement clause) and `BLOCKER_REASON_PRODUCERS` (now a map
  of write paths the invariant must survive, including the no-service-call path, rather than a patch
  list); `RED_COUNT_41` 13 -> 15
- `implementation-plan.md` - **new AC-41.14, AC-41.15**; AC-41.11 and AC-41.12 amended; three files
  added to MEU-41's Files Modified and the service row narrowed to one edit; two Spec Sufficiency rows
- `task.md` - row 6 rewritten for boundary enforcement, with the two new files in its durable outputs
  and anti-placeholder path set
- `correction-census.json` - five R8 values

**Execution gate:** satisfied by the user's explicit message, recorded above. Plan review ends here at
7 dispatched rounds; the next review artifact for this project will be the *execution* critical
review, dispatched after the MEU handoffs exist.

---

## Addendum — MEU renumber (2026-09-02, post-approval, pre-execution)

**What changed:** every Phase 10 MEU id shifted +1 — `MEU-40..MEU-48` became **`MEU-41..MEU-49`** — and
the session numbers shifted the same way (`19/20/21` -> **`20/21/22`**). AC prefixes moved with their
MEU: **old `AC-4X.N` == new `AC-4(X+1).N`** for X in 0..3 (e.g. old `AC-40.7` is now `AC-41.7`,
old `AC-43.16` is now `AC-44.16`). Matrix rows `10.1..10.9` and their MEU ids moved likewise.

**Why:** `MEU-40` was claimed on 2026-09-01 by the concurrent `p9-capture-native-picker` session
(`.agent/context/meu-status.yaml`, slug `native-region-picker`, matrix `9.7`, `status: in_progress`)
while this plan was in review round 7. Phase 10 therefore starts at `MEU-41`, and Phase 10's first
session is Session 20 because that session took Session 19.

**Reading rounds R1-R7 against the current plan:** the seven review-round prompts and every verdict
above use the pre-shift ids and were deliberately left unmodified as historical record. Apply the
`+1` mapping when tracing any finding to its current AC. No finding's substance, count, or
resolution changed — only the numeric label.

**Verification after the shift:** 624 substitutions across the plan folder + grouping doc, then
`run-correction-census.ps1` -> `PASS: CORRECTION_CENSUS` (45 values changed, 269 literals swept,
526 sites) with per-MEU RED predicates `41|8|8|MATCH`, `42|15|15|MATCH`, `43|13|13|MATCH`,
`44|16|16|MATCH`; transitive binding census -> `top-level keys: 196 | bound: 196 | UNBOUND: 0`,
`DANGLING citations: 0`. Zero residual `MEU-40|AC-40|meu-40|_40|WP-40` tokens in this plan's
artifacts. `_context.RED_TOTAL` corrected 43 -> 52 (8+15+13+16) — a pre-existing staleness the
censuses did not cover because it is nested and uncited.
