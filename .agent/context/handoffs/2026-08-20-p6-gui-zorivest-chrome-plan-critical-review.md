---
date: "2026-08-20"
review_mode: "plan"
round: 3
review_round: 3
target_plan: "docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: "GPT-5.6-sol"
---

# Critical Review: 2026-08-20-p6-gui-zorivest-chrome

> **Review Mode**: `plan`
> **Verdict**: `changes_required`

## Intent Anchor

Executing this plan is supposed to deliver MEU-26 only: Zorivest-derived av-kit shell chrome, including tokens, rail/header organization, a closed-by-default right console drawer, Settings chrome, written-and-wired Electron E2E coverage, and synchronized canonical documentation without implementing MEU-21–25. As written, the product intent is mostly specified, but the task sequence cannot reach H1 review and two validation owners can approve materially missing deliverables.

---

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **The SSOT sequence is impossible.** Row 1 changes YAML/generated inputs and explicitly forbids `render` until H1. H1-3 then updates YAML again and runs only `render --check`. The helper proves `update` calls `save(data)` only, while `render --check` calls `check_drift()` and never regenerates Markdown. Therefore H1-3 must fail on the drift introduced by rows 1/7 before the handoff/review barrier can be reached. This violates dependency/order correctness and PR-4. | `task.md:44`, `task.md:55`; `tools/meu_status.py:129-156` | Add the registered non-check `meu_status.py render` at H1 after the final pre-review YAML update and before `render --check`; keep the generated-doc assertions after that render. | open |
| 2 | High | High | **`E2E_CONTROL_CENSUS` false-passes materially absent E2 behavior.** The plan promises C1-1 closed launch, C1-3 expand/collapse geometry, C1-4 X/collapse/Escape closure, C1-5 Copy/log-to-file behavior, and C1-6 rail interaction. The executable owner checks only method-name adjacency: C1-1 accepts any `toHaveCount(...)` value; C1-3 accepts generic visibility instead of geometry/restore; C1-4 has no post-close oracle and does not require Escape or header-toggle closure; C1-5 requires only visibility, not click/clipboard/PUT; C1-6 requires only visibility, not rail-collapse interaction. Because an unavailable Electron run may be validly `[B]`, this static gate is the required written-and-wired proof and can currently approve tests that omit the promised behavior. This violates create-plan §4A.3, E2, PR-4, and PR-8 observable/negative-oracle binding. | `implementation-plan.md:114`; `task.md:47`; `assert-e2e-control-census.ps1:88-115`; `.agent/workflows/create-plan.md:258`; `.agent/docs/emerging-standards.md:1167-1185` | Strengthen the owner to bind each named case to its required action and outcome, including exact closed count, drawer width/full/restore geometry, all close paths with an absent-panel oracle, Copy/PUT effects, and rail-collapse state/geometry. | open |
| 3 | High | High | **The canonical GUI-spec amendment gate false-passes the required token/rail update.** Row 5 claims it proves bottom-dock replacement, `TOKEN_SET`, rail ASCII, and action-index rows, but its `06-gui.md` predicate checks only that one bottom-dock phrase is absent and that the unanchored case-insensitive word fragment `right` occurs anywhere. Existing `Bright Red` already satisfies that second check, and the command never asserts the replacement of the old `#1a1b26` design token or purple active-rail accent. The row can therefore pass while the canonical spec still contradicts the delivered chrome. This violates PR-4, PR-8, and DR-4. | `implementation-plan.md:62`; `task.md:48`; `docs/build-plan/06-gui.md:222`, `docs/build-plan/06-gui.md:271`, `docs/build-plan/06-gui.md:317` | Bind the predicate to the specific shell/console sections and required replacement tokens/rail text; distinguish the active-rail purple occurrence from unrelated status-color uses. | open |
| 4 | Low | High | **The unstarted task is labeled `in_progress`.** Every task row is unchecked, MEU-26 is not registered, the canonical review file did not exist before this pass, and the static trace sweep found no MEU-26 implementation artifacts outside the plan folder. This is clerical status drift and does not itself block. | `task.md:5` | Set the task frontmatter to the repository's unstarted-plan status convention. | open |

---

## Scope

**Targets**:

- `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/task.md`

**Authority and validation owners read**:

- `docs/build-plan/06-gui.md`
- `docs/build-plan/gui-actions-index.md`
- `.agent/docs/emerging-standards.md` (G11, G30-G36, E2)
- `.agent/context/meu-status.yaml`
- `GUARDRAILS.md` SIGN 1
- `.agent/workflows/create-plan.md` §4A
- the three plan-local `assert-*.ps1` owners and named helper `--help` surfaces

**Scope lock applied**: MEU-26 chrome only. MEU-21-25 implementation was not required or reviewed as a prerequisite. No product, plan, task, test, or canonical-spec file was edited.

---

## Commands Executed

Static evidence only, with receipts under `C:/Temp/av-kit/`:

- `Test-Path` census for all three plan-local assertion scripts, named helper owners, closeout templates/schema, grouping/matrix/metrics/OpenAPI artifacts, and the canonical review path.
- `rg` reads/sweeps over the plan, task, GUI authority, action index, emerging standards, MEU registry, helper source, and unstarted implementation traces.
- `uv run python tools/check_exec_review.py --help`
- `uv run python tools/export_openapi.py --help`
- `uv run python tools/meu_status.py --help`, `update --help`, and `render --help`

No pytest, Vitest, Playwright, build, lint, typecheck, render, update, or other project mutation command was run.

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-26.1-26.18 each names Spec, Local Canon, Research-backed, Human-approved, or an explicit carry-forward owner. |
| Validation cells are exact commands | fail | Commands are concrete, but Findings 1-3 show one impossible sequence and two demonstrated false-passing predicates. |
| BUILD_PLAN audit row present | pass | Numeric row 7 owns plan binding, phase-plan preservation, and the hub Next field. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows are explicit and ordered. |
| Referenced artifacts exist before flag review | pass | All three `assert-*.ps1` files and all named helper owners tested `True`; supported CLI flags were confirmed only after existence. |

### Design Review (DR-1-DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The plan describes an unstarted change; the trace sweep found no MEU-26 implementation outside the plan folder. |
| DR-2 Residual old terms | pass | Bottom-dock/old-token terms remain only in pre-execution canon and are explicitly scheduled for supersession; Finding 3 addresses proof quality. |
| DR-3 Downstream references updated | pass | The plan owns both `06-gui.md` and `gui-actions-index.md` updates. |
| DR-4 Verification robustness | fail | Findings 2-3 demonstrate false-passing E2E and documentation gates. |
| DR-5 Evidence auditability | pass | Commands and receipt paths are concrete and reproducible. |
| DR-6 Cross-reference integrity | pass | Human-approved console/token overrides are identified and paired with canonical-spec amendments. |
| DR-7 Evidence freshness | n/a | No implementation or passing-test count is claimed in this unstarted plan. |
| DR-8 Completion vs residual risk | pass | Neither target claims implementation completion. |

### Plan Review (PR-1-PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass with Low note | Scope, order, outputs, and MEU-26 lock align; only task frontmatter status drifts (Finding 4). |
| PR-2 Not-started confirmation | pass | All rows are unchecked; MEU-26 is planned but absent from `meu-status.yaml`; no implementation traces were found. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, validation, dependency/context, and status. |
| PR-4 Validation realism | fail | Findings 1-3 are execution-blocking or materially false-passing. |
| PR-5 Source-backed planning | pass | Non-spec behavior is labeled Local Canon, Research-backed, Human-approved, or explicit carry-forward. |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff and one rolling implementation-review path are explicit; Round 1 has no correction-census precondition. |
| PR-7 Scope discipline / C2 | pass | Deferred MEU-21, MEU-22, and MEU-23 exist in the registry; remaining out-of-scope rows cite current focus, grouping, GUI spec, G33, approved MEU-20, or the av-kit domain boundary. MEU-26 registration is an explicit first task. |
| PR-8 Control reachability and totality | fail | Core AppShell event/persist/poll chains are named, but the executable E2/static documentation controls do not bind the promised observables and negative outcomes (Findings 2-3). |
| PR-9 Single-statement discipline | pass | Material sets, thresholds, events, paths, and caps are named once and referenced; no materially divergent live spelling was found. |

### create-plan §4A GUI Compliance

| Check | Result | Evidence |
|-------|--------|----------|
| Substitute control mapping | pass | The plan §4A table maps controls to test IDs, variants/sizes/states, feedback tiers, and E2E cases because the canonical indexes are absent. |
| G30-G35 plan coverage | pass | SelectInput/G30, unified accent, token-only classes, motion constraints, Button variants, and feedback tiers are represented in named sets/ACs. |
| E2 written-and-wired proof | fail | The cases are named, but the sole census owner can approve materially missing interactivity and visual outcomes (Finding 2). |
| G36 protection | pass | Unit runs use `--allowOnly=false`; the plan includes static skip/only/todo scanning and forbids test neutralization. |

---

## Open Questions / Assumptions

- No human-decision question remains for this review. The plan's recorded 2026-08-20 Human-approved console placement, token choice, default-closed behavior, and MEU-26 insertion were treated as authoritative planning inputs.
- MEU-26 being absent from `meu-status.yaml` is intentional pre-execution state because task row 1 owns registration; MEU-21-25 implementation is outside this review.

---

## Verdict

`changes_required` — Findings 1-3 meet the workflow's blocking threshold: the plan cannot reach its review barrier as sequenced, and two gates demonstrably false-pass materially missing GUI/E2/canonical-doc deliverables. Route corrections through `/plan-corrections`; do not begin MEU-26 execution from this Round 1 plan.

## Concrete Follow-up Actions

1. Repair the H1 SSOT render/update/check sequence.
2. Bind `assert-e2e-control-census.ps1` to the exact promised actions and negative/visual outcomes.
3. Replace the row-5 broad documentation predicate with section- and token-specific assertions.
4. Correct the clerical unstarted task status.
5. Return the corrected plan through Round 2 with the required untruncated, per-hit-disposition blast-radius census.

## Residual Risk

This was intentionally a static plan review. Runtime UI behavior, helper execution beyond `--help`, and test outcomes remain unverified and must be established during TDD/execution after plan approval.

---

## Corrections Applied (2026-08-20) — after Round 1

**Workflow**: `/plan-corrections` inside `/create-plan` §5b (parent loop wins over `plan-corrections.md` HARD STOP). Plan/task + plan-folder helper scripts only. No product code.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Conflict flagged**: `plan-corrections.md` Step 7 / HARD STOP say timestamp-and-stop and do not chain into re-review; `create-plan.md` §5b requires blast-radius census then re-dispatch. Parent create-plan loop is followed.

Round-1 findings 1–4 addressed. F1–F4 are `fixed` (none refuted).

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| 1 | High | fixed | Named `SSOT_RENDER` (`meu_status.py render`, no `--check`). H1-3 now runs `SSOT_RENDER` → `SSOT_READY` → `render --check`. Row 1 still forbids render until H1. Receipt: `C:/Temp/av-kit/meu-render-h1.txt`. |
| 2 | High | fixed | `E2E_CASE_ORACLES` + stronger `assert-e2e-control-census.ps1`: C1-1 exact `toHaveCount(0)` (rejects `toHaveCount(1)`); C1-3 `w-full` + `min-w-[320px]`; C1-4 X + collapse + Escape + header toggle + post-close `toHaveCount(0)`; C1-5 copy/log-to-file `.click(` + `settings/app`/`log_to_file`/`clipboard`; C1-6 `nav-collapse` `.click(` + `nav-rail--collapsed`. |
| 3 | High | fixed | Named `SPEC_AMEND_MARKERS`. Row 5 no longer accepts the unanchored word `right` (Bright Red false-pass). Requires `CONSOLE PANEL (right side sheet`, `dark background (`#282a36`)`, `accent bar (cyan `#8be9fd``; forbids bottom-dock ASCII, `dark background (`#1a1b26`)`, and active-rail `purple `#bd93f9`` (status-legend `Purple (`#bd93f9`)` stays unrelated). Actions index still requires `console:toggle` / `console:expand` / `console:close`. |
| 4 | Low | fixed | `task.md` frontmatter `status: "draft"` to match the unstarted plan. |

### Declared variants swept

Old: `status: "in_progress"`, `06-gui missing right-side console`, `-notmatch 'right'`, `PLAN_FOLDER`; prove `SSOT_READY` then `render --check`, `Assert-HasBound $c5 'console-copy' $visual`.
New / semantic: `SSOT_RENDER`, `SPEC_AMEND_MARKERS`, `E2E_CASE_ORACLES`, `toHaveCount(0)`, `meu-render-h1`, `nav-rail--collapsed`, `CONSOLE PANEL (right side sheet`, `status: "draft"`, `accent bar (cyan`, `dark background (`#282a36`)`, `clipboard`.

Manifest: `C:/Temp/av-kit/census-p6-chrome-r1-manifest.txt`. Runner: `C:/Temp/av-kit/census-p6-chrome-r1-run.txt`. Scripts exist: `assert-red-oracle.ps1`, `assert-e2e-control-census.ps1`, `assert-handoff-markers.ps1`.

Blast-radius census: 5 old + 11 new = 16 sweeps. Zero-hit old receipts: 5. Nonzero raw `file:line` hits: 33. Each hit dispositioned below. No truncated `Select-Object -First` / `head`.

### Zero-hit old receipts (stale gone)

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-chrome-r1-old-status-in-progress.txt` | 0 | no stale `status: "in_progress"` |
| `C:/Temp/av-kit/census-p6-chrome-r1-old-right-falsepass-msg.txt` | 0 | no stale Bright-Red-passing error string |
| `C:/Temp/av-kit/census-p6-chrome-r1-old-notmatch-right.txt` | 0 | no unanchored `-notmatch 'right'` |
| `C:/Temp/av-kit/census-p6-chrome-r1-old-h13-no-ssot-render.txt` | 0 | no H1-3 that checks drift without `SSOT_RENDER` |
| `C:/Temp/av-kit/census-p6-chrome-r1-old-c15-copy-visual-only.txt` | 0 | no C1-5 copy visibility-only bind |

### Per-hit disposition — `SSOT_RENDER` (2)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-ssot-render.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:55` | updated — H1-3 names and runs `SSOT_RENDER` before `--check` |
| 2 | `implementation-plan.md:118` | updated — named-set definition |

### Per-hit disposition — `SPEC_AMEND_MARKERS` (3)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-spec-amend-markers.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — row 5 proves the named set |
| 2 | `implementation-plan.md:62` | updated — WP-26e cites the set |
| 3 | `implementation-plan.md:119` | updated — named-set definition |

### Per-hit disposition — `E2E_CASE_ORACLES` (5)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-e2e-case-oracles.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:1` | updated — executable owner header |
| 2 | `task.md:47` | updated — row 4 requires the set |
| 3 | `implementation-plan.md:61` | updated — WP-26d cites the set |
| 4 | `implementation-plan.md:117` | updated — named-set definition |
| 5 | `implementation-plan.md:120` | updated — `E2E_CONTROL_CENSUS` names the owner |

### Per-hit disposition — `toHaveCount(0)` (6)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-tohavecount-0.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:68` | updated — exact-zero literal |
| 2 | `assert-e2e-control-census.ps1:71` | updated — rejects `toHaveCount(1)` |
| 3 | `assert-e2e-control-census.ps1:140` | updated — C1-4 post-close oracle |
| 4 | `implementation-plan.md:114` | updated — `E2E_CASES` C1-1/C1-4 |
| 5 | `implementation-plan.md:116` | updated — `E2E_PER_CONTROL` closed oracle |
| 6 | `implementation-plan.md:117` | confirmed-consistent — `E2E_CASE_ORACLES` restates the same zero |

### Per-hit disposition — `meu-render-h1` (1)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-meu-render-h1.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:55` | updated — H1-3 render receipt path |

### Per-hit disposition — `nav-rail--collapsed` (4)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-nav-rail-collapsed.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:155` | updated — C1-6 class oracle |
| 2 | `implementation-plan.md:93` | confirmed-consistent — pre-existing `RAIL_COLLAPSED_PX` class name |
| 3 | `implementation-plan.md:114` | updated — `E2E_CASES` C1-6 |
| 4 | `implementation-plan.md:117` | confirmed-consistent — `E2E_CASE_ORACLES` C1-6 |

### Per-hit disposition — `CONSOLE PANEL (right side sheet` (2)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-right-side-sheet.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — row 5 required replacement |
| 2 | `implementation-plan.md:119` | confirmed-consistent — `SPEC_AMEND_MARKERS` definition |

### Per-hit disposition — `status: "draft"` (2)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-status-draft.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:5` | updated — unstarted convention |
| 2 | `implementation-plan.md:6` | confirmed-consistent — plan was already draft |

### Per-hit disposition — `accent bar (cyan` (1)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-accent-cyan.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:119` | updated — rail-accent replacement in `SPEC_AMEND_MARKERS` |

### Per-hit disposition — `dark background (\`#282a36\`)` (2)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-dark-bg-282a36.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — row 5 design-basis replacement |
| 2 | `implementation-plan.md:119` | confirmed-consistent — `SPEC_AMEND_MARKERS` definition |

### Per-hit disposition — `clipboard` (5)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r1-new-clipboard-c15.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:147` | updated — C1-5 effect alternative |
| 2 | `assert-e2e-control-census.ps1:148` | confirmed-consistent — error text for the same alternative |
| 3 | `implementation-plan.md:114` | updated — `E2E_CASES` C1-5 |
| 4 | `implementation-plan.md:117` | confirmed-consistent — `E2E_CASE_ORACLES` C1-5 |
| 5 | `implementation-plan.md:198` | confirmed-consistent — AC-26.18 already named clipboard write |

Ready for independent Round 2. Reviewer must write **new first frontmatter** `round: 2` / `review_round: 2` and adjudicate F1–F4 plus PR-6 census completeness. Do not treat this `corrections_applied` as `approved`.

---

## Recheck (2026-08-20) — Round 2

**Workflow**: `/plan-critical-review`
**Agent**: GPT-5.6-sol

### Intent Anchor

Executing this plan is supposed to deliver MEU-26 only: Zorivest-derived av-kit shell chrome, including tokens, rail/header organization, a closed-by-default right console drawer, Settings chrome, written-and-wired Electron E2E coverage, and synchronized canonical documentation without implementing MEU-21–25. As corrected, the SSOT sequence and unstarted status are sound, but the static E2 owner and canonical-spec amendment gate can still approve materially incomplete deliverables.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **Round 1 F2 remains open: `E2E_CONTROL_CENSUS` still false-passes missing promised outcomes.** C1-1 binds `console-panel` to any `toHaveCount` and checks `toHaveCount(0)` separately, so `console-panel.toHaveCount(1)` plus an unrelated zero-count assertion passes. C1-4 requires all four action literals but only one zero-count literal anywhere in the case, while `E2E_CASES` requires each close path to end absent. C1-5 requires both clicks but accepts any one of `settings/app`, `log_to_file`, or `clipboard`, while AC-26.18 requires both a clipboard write and the log-to-file PUT. Because the Electron run may be validly `[B]`, these are concrete static-gate false-passes for materially missing E2 behavior, violating create-plan §4A.3, E2, PR-4, and PR-8. | `assert-e2e-control-census.ps1:117-121`, `assert-e2e-control-census.ps1:134-150`; `implementation-plan.md:114`, `implementation-plan.md:198` | Bind exact zero count to the `console-panel` locator; require a distinct absent-panel assertion after each C1-4 close path; require separate clipboard and `/settings/app` PUT effects for C1-5. | open |
| 2 | High | High | **Round 1 F3 remains open: `SPEC_AMEND_MARKERS` can pass while the canonical console contract still says bottom dock.** The plan itself says to amend `06-gui.md` lines 248–253 and 308–327, but task row 5 schedules only the ASCII replacement and its predicate forbids only the exact ASCII phrase. It does not reject the existing `Console Panel (Bottom Dock)` heading, `docked to the bottom` prose, or height-persistence contract; the action index can also retain `console:collapse` as a `Dock toggle` while merely adding the three new IDs. Thus the gate can pass while canonical docs materially contradict `CONSOLE_SIDE_SHEET`, violating PR-1, PR-4, PR-8, DR-3, DR-4, and DR-6. | `implementation-plan.md:74`, `implementation-plan.md:119`; `task.md:48`; `docs/build-plan/06-gui.md:308`, `docs/build-plan/06-gui.md:312`, `docs/build-plan/06-gui.md:327`; `docs/build-plan/gui-actions-index.md:68` | Make row 5 own the complete 308–327 side-sheet supersession and the existing collapse-row semantic update; make the gate reject those stale section/index contracts, not only the ASCII label. | open |

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|--------------|----------------|
| F1 — impossible SSOT sequence | open | ✅ Fixed — H1-3 now runs non-check `SSOT_RENDER` after the ready-for-review mutation and before `render --check`; current helper source confirms `update` only saves and non-check `render` regenerates. |
| F2 — E2 census false-pass | open | ❌ Still open — Finding 1 demonstrates three original promised behaviors remain unbound. |
| F3 — spec-amend false-pass | open | ❌ Still open — Finding 2 demonstrates the corrected gate still permits contradictory bottom-dock canon. |
| F4 — unstarted status | open | ✅ Fixed — both plan and task frontmatter are `draft`; every actionable task row remains `[ ]`. |

### PR-6 Blast-Radius Census Gate

**Pass.** All 18 named receipt files exist. The manifest and runner are untruncated; five obsolete-pattern receipts are empty with recorded `rg rc=1`; the 11 nonzero sweeps inventory 33 raw `file:line` hits. The Corrections Applied appendix assigns every hit `updated` or `confirmed-consistent`. The appendix was treated only as correction evidence, never as approval.

### Scope

**Targets reviewed**:

- `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/assert-e2e-control-census.ps1`

**Authority reviewed**: `docs/build-plan/06-gui.md` (layout, console, Settings, E2E waves), `docs/build-plan/gui-actions-index.md`, `.agent/docs/emerging-standards.md` (G11, G30–G36, E2), `.agent/context/meu-status.yaml`, `.agent/workflows/create-plan.md` §4A, and `GUARDRAILS.md` SIGN 1.

**Scope lock applied**: MEU-26 chrome only. MEU-21–25 implementation was not required. No UI suite or project mutation command was run, and no product, plan, task, test, or canonical-spec file was edited.

### Commands Executed

Static evidence only, with receipts under `C:/Temp/av-kit/`:

- `Test-Path` for all 18 census receipts, the rolling review, three plan-local `assert-*.ps1` owners, named helper owners, templates/schema, grouping/matrix/metrics/OpenAPI artifacts, GUI indexes, and correlated implementation handoffs.
- Untruncated reads of the census manifest/runner/raw hit receipts and per-hit dispositions.
- Numbered file reads and `rg` sweeps over the plan, task, E2 census owner, GUI canon, action index, emerging standards, MEU registry, grouping/matrix, helper source, repeated terms, and unstarted task state.
- `uv run python tools/meu_status.py --help`, `update --help`, `render --help`; `tools/check_exec_review.py --help`; `tools/export_openapi.py --help`.

No pytest, Vitest, Playwright, build, lint, typecheck, render, update, OpenAPI export/check, or other project execution command was run.

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-26.1–26.18 each names an allowed Spec, Local Canon, Research-backed, Human-approved, or explicit carry-forward basis. |
| Validation cells are exact commands | fail | Commands are concrete and supported, but Findings 1–2 demonstrate materially false-passing predicates. |
| BUILD_PLAN audit row present | pass | Numeric row 7 owns MEU/phase-plan binding and the hub Next field; H1-3 owns the post-mutation render. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows are explicit and ordered. |
| Referenced artifacts exist before flag review | pass | All three plan-local assertions and every named helper owner tested `True`; supported flags were checked only afterward via `--help`. |

#### Design Review (DR-1–DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The plan remains unstarted: every actionable row is `[ ]`; MEU-26 is absent from the registry; no MEU-26 implementation handoff/review exists. |
| DR-2 Residual old terms | fail | Finding 2 shows the planned proof allows the heading/prose/height bottom-dock contract to survive. |
| DR-3 Downstream references updated | fail | Adding new action IDs does not require updating the existing stale `console:collapse` dock row (Finding 2). |
| DR-4 Verification robustness | fail | Findings 1–2 demonstrate concrete false-passes. |
| DR-5 Evidence auditability | pass | Static commands, receipts, paths, and line references are reproducible. |
| DR-6 Cross-reference integrity | fail | The Human-approved side-sheet contract is not guaranteed to replace all contradictory canonical console text (Finding 2). |
| DR-7 Evidence freshness | pass | Census manifest counts reproduce: 5 zero-hit old sweeps and 33 dispositioned nonzero hits. |
| DR-8 Completion vs residual risk | pass | Neither target nor this review claims implementation completion. |

#### Plan Review (PR-1–PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | fail | Plan line 74 owns the full 308–327 supersession; task row 5 narrows the action/proof to ASCII plus marker presence (Finding 2). |
| PR-2 Not-started confirmation | pass | All actionable rows are unchecked; MEU-26 is planned but not registered; correlated implementation artifacts are absent. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, validation, dependency/context, durable output, and status. |
| PR-4 Validation realism | fail | Findings 1–2 are materially false-passing static gates. |
| PR-5 Source-backed planning | pass | Non-spec behavior is labeled Local Canon, Research-backed, Human-approved, or explicit carry-forward. |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff and one rolling implementation-review path are explicit; the Round 2 census procedural gate passes. |
| PR-7 Scope discipline / C2 | pass | Deferred MEU-21–23 exist; MEU-24–25 remain registered/pending; out-of-scope rows cite the GUI spec, G33, current focus/grouping, approved MEU-20, or the av-kit domain boundary. MEU-26 registration is explicit row 1 work. |
| PR-8 Control reachability and totality | fail | Findings 1–2 demonstrate promised observables can be absent while the asserted controls pass. |
| PR-9 Single-statement discipline | pass | Named sets own the material thresholds/events/paths; no materially divergent live spelling outside Findings 1–2 was found. |

#### create-plan §4A GUI Compliance

| Check | Result | Evidence |
|-------|--------|----------|
| Substitute control mapping | pass | The canonical GUI reference/index files are absent; plan §4A maps controls to test IDs, variants/sizes/states, feedback tiers, and E2E cases. |
| G30–G35 plan coverage | pass | SelectInput/G30, unified accent, token-only classes, canonical motion, Button variants, and feedback tiers are represented. |
| E2 written-and-wired proof | fail | Finding 1 shows the sole static owner can approve materially incomplete behavior when Electron execution is `[B]`. |
| G36 protection | pass | Unit runs use `--allowOnly=false`; the plan includes static skip/only/todo scanning and forbids test neutralization. |

### Open Questions / Assumptions

- No human-decision question remains. The Human-approved MEU-26 insertion, side-sheet placement, cyan/Dracula token choice, and default-closed behavior were treated as authoritative.
- The scope remains chrome only. This review did not require MEU-21–25 implementation or execute the UI suite.

### Verdict

`changes_required` — Findings 1–2 meet the blocking threshold: the corrected plan still contains two demonstrated false-passing gates that can approve materially missing E2 behavior and a materially contradictory canonical console contract. Route fixes through `/plan-corrections`; do not begin MEU-26 execution from this Round 2 plan.

### Concrete Follow-up Actions

1. Finish F2 by binding C1-1 zero count to `console-panel`, asserting absence after every C1-4 close path, and independently proving both C1-5 effects.
2. Finish F3 by making the full console section and existing collapse action row conform to `CONSOLE_SIDE_SHEET`, with stale-contract rejection in `SPEC_AMEND_MARKERS`.
3. Return through Round 3 with the required untruncated, per-hit-disposition correction census.

### Residual Risk

This was intentionally a static plan review. Runtime Electron behavior, test outcomes, and helper execution beyond `--help` remain unverified and belong to TDD/execution only after plan approval.

---

## Corrections Applied (2026-08-20) — after Round 2

**Workflow**: `/plan-corrections` inside `/create-plan` §5b (parent loop wins over `plan-corrections.md` HARD STOP). Plan/task + plan-folder helper scripts only. No product code.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Conflict flagged**: same parent-loop override as after Round 1.

Round-2 findings 1–2 addressed. Both are `fixed` (none refuted). This is the last plan-review round before the cap (3).

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| 1 | High | fixed | C1-1 now requires same-expression `console-panel` `.toHaveCount(0)` (`Test-HasBound`); unrelated `toHaveCount(0)` fails the helper self-test. C1-4 requires `Get-BoundMatchCount` ≥ 4 **and** `Assert-C14EachPathEndsAbsent` (each close-path window must contain a bound zero). A four-action + one-trailing-zero fixture must throw. C1-5 requires `clipboard` **and** `settings/app` **and** `log_to_file` (no OR). |
| 2 | High | fixed | `SPEC_AMEND_MARKERS` + task row 5 now own ASCII 248–253 **and** section 308–327 **and** the collapse-row semantic. Gate rejects `Console Panel (Bottom Dock)`, `docked to the bottom`, `ui.panel.console.height`, and `Dock toggle`. Requires `Console Panel (Right Side Sheet)` and `ui.panel.console.visible`. |

### Declared variants swept

Old: `settings/app|log_to_file|clipboard`, `C1-4 missing post-close toHaveCount(0) oracle`, `Assert-HasBound $c1 'console-panel' 'toHaveCount'`, `Get-BoundCount`.
New / semantic: `Get-BoundMatchCount`, `Assert-C14EachPathEndsAbsent`, `toHaveCount\(0\)`, `Console Panel (Bottom Dock)`, `docked to the bottom`, `ui.panel.console.height`, `Dock toggle`, `Console Panel (Right Side Sheet)`, `ui.panel.console.visible`, `-lt 4`.

Manifest: `C:/Temp/av-kit/census-p6-chrome-r2-manifest.txt`. Runner: `C:/Temp/av-kit/census-p6-chrome-r2-run.txt`.

Blast-radius census: 4 old + 10 new = 14 sweeps. Zero-hit old receipts: 4. Nonzero raw `file:line` hits: 36. Each hit dispositioned below. No truncated `Select-Object -First` / `head`.

### Zero-hit old receipts (stale gone)

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-chrome-r2-old-c15-or-effects.txt` | 0 | no C1-5 OR-effects predicate |
| `C:/Temp/av-kit/census-p6-chrome-r2-old-c14-one-zero.txt` | 0 | no single-oracle C1-4 error |
| `C:/Temp/av-kit/census-p6-chrome-r2-old-c11-any-count.txt` | 0 | no unbound any-`toHaveCount` C1-1 |
| `C:/Temp/av-kit/census-p6-chrome-r2-old-get-bound-count.txt` | 0 | stale helper name removed |

### Per-hit disposition — `Get-BoundMatchCount` (4)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-get-bound-match-count.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:44` | updated — helper definition |
| 2 | `assert-e2e-control-census.ps1:200` | updated — C1-4 count ≥ 4 |
| 3 | `implementation-plan.md:116` | updated — `E2E_PER_CONTROL` owner |
| 4 | `implementation-plan.md:117` | confirmed-consistent — `E2E_CASE_ORACLES` cites the same helper |

### Per-hit disposition — `Assert-C14EachPathEndsAbsent` (5)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-c14-each-path.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:58` | updated — per-path window helper |
| 2 | `assert-e2e-control-census.ps1:128` | updated — false-pass fixture must throw |
| 3 | `assert-e2e-control-census.ps1:204` | updated — live C1-4 call |
| 4 | `implementation-plan.md:116` | updated — owner named |
| 5 | `implementation-plan.md:117` | confirmed-consistent — `E2E_CASE_ORACLES` |

### Per-hit disposition — `toHaveCount\(0\)` (5)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-bound-zero-regex.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:59` | updated — per-path zero regex |
| 2 | `assert-e2e-control-census.ps1:110` | updated — C1-1 unrelated-zero reject |
| 3 | `assert-e2e-control-census.ps1:114` | updated — C1-1 same-expression accept |
| 4 | `assert-e2e-control-census.ps1:182` | updated — live C1-1 bind |
| 5 | `assert-e2e-control-census.ps1:200` | confirmed-consistent — C1-4 count uses the same regex |

### Per-hit disposition — `Console Panel (Bottom Dock)` (2)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-heading-bottom-dock.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:119` | updated — forbid in `SPEC_AMEND_MARKERS` |
| 2 | `task.md:48` | updated — row 5 stale list |

### Per-hit disposition — `docked to the bottom` (2)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-docked-to-bottom.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — row 5 stale list |
| 2 | `implementation-plan.md:119` | confirmed-consistent — `SPEC_AMEND_MARKERS` |

### Per-hit disposition — `ui.panel.console.height` (6)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-height-persist.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — row 5 forbids the height key in `06-gui.md` |
| 2 | `implementation-plan.md:74` | confirmed-consistent — lock 3 names the key being superseded |
| 3 | `implementation-plan.md:103` | confirmed-consistent — `PERSIST_UI_KEYS` explicitly excludes it |
| 4 | `implementation-plan.md:119` | updated — `SPEC_AMEND_MARKERS` forbid |
| 5 | `implementation-plan.md:192` | confirmed-consistent — AC-26.12 negative |
| 6 | `implementation-plan.md:206` | confirmed-consistent — control-binding negative |

### Per-hit disposition — `Dock toggle` (3)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-dock-toggle.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — row 5 forbids the action-index label |
| 2 | `implementation-plan.md:62` | updated — WP-26e owns the semantic change |
| 3 | `implementation-plan.md:119` | confirmed-consistent — `SPEC_AMEND_MARKERS` |

### Per-hit disposition — `Console Panel (Right Side Sheet)` (2)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-heading-right-sheet.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — required heading |
| 2 | `implementation-plan.md:119` | confirmed-consistent — `SPEC_AMEND_MARKERS` |

### Per-hit disposition — `ui.panel.console.visible` (6)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-visible-persist.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — required persist replacement |
| 2 | `implementation-plan.md:102` | confirmed-consistent — `CONSOLE_DEFAULT_CLOSED` |
| 3 | `implementation-plan.md:103` | confirmed-consistent — `PERSIST_UI_KEYS` |
| 4 | `implementation-plan.md:119` | updated — `SPEC_AMEND_MARKERS` require |
| 5 | `implementation-plan.md:171` | confirmed-consistent — persist control table |
| 6 | `implementation-plan.md:206` | confirmed-consistent — AC-26.12 binding |

### Per-hit disposition — `-lt 4` (1)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-c14-four-bound.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:200` | updated — C1-4 bound-oracle threshold |

### Per-hit disposition — `Side-sheet collapse` (2)

Receipt: `C:/Temp/av-kit/census-p6-chrome-r2-new-side-sheet-collapse.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — row 5 requires the collapse-row replacement trigger |
| 2 | `implementation-plan.md:119` | updated — `SPEC_AMEND_MARKERS` requires `console:collapse` and `Side-sheet collapse` |

### Per-hit disposition — C1-5 AND error strings (2)

Receipts: `C:/Temp/av-kit/census-p6-chrome-r2-new-c15-clipboard-and.txt`, `C:/Temp/av-kit/census-p6-chrome-r2-new-c15-settings-app.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:210` | updated — clipboard is a required effect, not an OR alternative |
| 2 | `assert-e2e-control-census.ps1:214` | updated — `settings/app` PUT path is a required effect |

Authoritative extra runner: `C:/Temp/av-kit/census-p6-chrome-r2-manifest.txt` (5 old zero-hit + 9 new). Old receipts with `rg_rc=1` (file:line hits = 0; banner-only): `old-c11-loose-tohavecount`, `old-c15-or-predicate`, `old-c14-single-zero`, `old-e2e-cases-or`, `old-c15-or-error`.

Ready for independent Round 3 (plan-review cap). Reviewer must write **new first frontmatter** `round: 3` / `review_round: 3` and adjudicate r2 F1–F2 plus PR-6 on this census. Do not treat this `corrections_applied` as `approved`.

---

## Recheck (2026-08-20) — Round 3 (Plan-Review Cap)

**Workflow**: `/plan-critical-review`  
**Agent**: `GPT-5.6-sol`  
**Review Mode**: `plan`  
**Verdict**: `approved`

### Scope

**Targets reviewed (read-only)**:

- `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/assert-e2e-control-census.ps1`

**Authority reviewed**: `docs/build-plan/06-gui.md` (including lines 248–253 and 308–327), `docs/build-plan/gui-actions-index.md`, `.agent/docs/emerging-standards.md` (G11, G30–G36, E2), `.agent/context/meu-status.yaml`, `.agent/workflows/create-plan.md` §4A, `GUARDRAILS.md` SIGN 1, the current Electron E2E specs invoked by task row 4, and the named local Zorivest source owners.  
**Checklist Applied**: IR; DR-1–DR-8; PR-1–PR-9; Round-3 PR-6 pre-verdict gate; C2 Out of Scope; create-plan §4A GUI compliance.  
**Scope Lock**: MEU-26 chrome only. MEU-21–25 implementation, product changes, plan corrections, and UI-suite execution were excluded.

### PR-6 Pre-Verdict Gate

`PASS`. All 16 receipts named in the Round-3 request exist and are untruncated. The four obsolete-pattern receipts have `rg_rc=1` and zero raw `file:line` hits; their `hit_count=1` values are the RTK banner only. The ten new primary sweeps inventory 36 raw `file:line` hits, and the after-Round-2 appendix assigns every hit an `updated` or `confirmed-consistent` disposition.

The manifest's additional 14-child runner set was also read directly: all children exist, five old sweeps have zero source hits, and the nine new sweeps contain 20 overlapping live hits covered by the same disposition tables. `census-p6-chrome-r2-run.txt` reports `PASS: census-p6-chrome-r2-runner`. The appendix was treated solely as correction evidence, never as a verdict or approval signal.

### Intent Anchor

Executing this plan is supposed to deliver MEU-26 only: Zorivest-derived av-kit shell chrome with Dracula/cyan tokens, pinned rail/header organization, a closed-by-default right-side console sheet, Settings chrome, written-and-wired Electron E2E coverage, and synchronized canonical documentation without implementing MEU-21–25. The Round-2 corrections now bind the previously missing E2 outcomes and the complete bottom-dock-to-side-sheet canonical-spec supersession, so the plan is executable as written for that objective.

### Findings

No Critical, High, Medium, or Low findings.

### Round-2 Finding Adjudication

| Round-2 Item | Prior Status | Recheck Result | Evidence |
|--------------|--------------|----------------|----------|
| F1 — E2 static owner false-passed C1-1, C1-4, and C1-5 outcomes | open High | ✅ Fixed | C1-1 now requires same-expression `console-panel.toHaveCount(0)` and embeds an unrelated-receiver rejection (`assert-e2e-control-census.ps1:106-117,179-182`). C1-4 combines a bound-zero count of at least four with per-close-path windows and a four-actions/one-trailing-zero reject fixture (`assert-e2e-control-census.ps1:44-82,119-135,195-204`). C1-5 independently requires `clipboard`, `settings/app`, and `log_to_file` after both control clicks (`assert-e2e-control-census.ps1:206-219`). |
| F2 — spec-amend gate allowed contradictory bottom-dock canon | open High | ✅ Fixed | `SPEC_AMEND_MARKERS` and task row 5 now own both ASCII 248–253 and section 308–327 plus the existing `console:collapse` semantic. The predicate rejects `Console Panel (Bottom Dock)`, `docked to the bottom`, `ui.panel.console.height`, and `Dock toggle`, while requiring `Console Panel (Right Side Sheet)`, `ui.panel.console.visible`, `console:collapse`, and `Side-sheet collapse` (`implementation-plan.md:62,119`; `task.md:48`). |

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-26.1–26.18 each names Spec, Local Canon, Research-backed, Human-approved, or an explicit carry-forward/plan-lock basis. |
| Validation cells are exact commands | pass | Every actionable task row has a concrete redirected command and named receipt; current `meu_status.py`, `check_exec_review.py`, and `export_openapi.py` help surfaces support the referenced flags. |
| BUILD_PLAN audit row present | pass | Row 7 owns MEU/phase-plan binding and preserves `HUB_NEXT_AFTER`; H1-3 owns render-after-mutation and drift check. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows are explicit and correctly ordered. |
| Referenced artifacts exist before flag review | pass | All three plan-local `assert-*.ps1` owners, Python helper owners, dispatch owner, templates/schema, and grouping authority tested `True` before flags were assessed. |

#### Documentation Review (DR-1–DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The correction claims match the current plan/task/helper. Every actionable task row remains `[ ]`; MEU-26 and its implementation handoff/review/reflection remain absent. |
| DR-2 Residual old terms | pass | Old bottom-dock terms remain only as current canon to be replaced or as explicit negative/supersession text; row 5's predicate rejects them from the completed canonical docs. |
| DR-3 Downstream references updated | pass | WP-26e/task row 5 own both `06-gui.md` and the existing `gui-actions-index.md` collapse row plus new console action rows. |
| DR-4 Verification robustness | pass | The concrete Round-2 E2 and spec-amend false passes are now rejected by the executable/static predicates. |
| DR-5 Evidence auditability | pass | Primary receipts, manifest children, per-hit dispositions, line-numbered targets, existence checks, and help receipts are reproducible. |
| DR-6 Cross-reference integrity | pass | Plan, task, E2 owner, side-sheet lock, persistence keys, spec-amend markers, G11 owner, and action-index semantics agree. |
| DR-7 Evidence freshness | pass | Round-2 census receipts and the current corrected targets were re-read in this pass; no appendix claim was accepted without file-state confirmation. |
| DR-8 Completion vs residual risk | pass | The plan remains draft/unstarted and does not claim implementation or runtime completion. |

#### Plan Review (PR-1–PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | WP-26a–g aligns with numeric rows 1–7 and the H1→review→H2 sequence; row 5 now carries the complete WP-26e contract. |
| PR-2 Not-started confirmation | pass | All actionable rows are `[ ]`; MEU-26 is not yet registered; the MEU handoff, implementation review, and reflection do not exist. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, validation, dependency, context strategy, durable outputs, builder model, and status. |
| PR-4 Validation realism | pass | The corrected E2 owner binds the exact Round-2 outcomes, and the spec-amend gate rejects the materially contradictory canonical state. |
| PR-5 Source-backed planning | pass | Non-spec behavior resolves to Human-approved decisions, local Zorivest canon, Research-backed accessibility/layout sources, or named local standards. |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff and one rolling implementation-review path are explicit; all requested and manifest-child census receipts are present, untruncated, and dispositioned. |
| PR-7 Scope discipline / C2 | pass | Deferred MEU-21–23 exist in `meu-status.yaml`; MEU-24–25 remain pending; every out-of-scope row cites the GUI spec, G33, current-focus/grouping, approved MEU-20, or the av-kit domain boundary. MEU-26 registration is explicit row-1 work. |
| PR-8 Control reachability and totality | pass | `AppShell` is the always-mounted G11 owner; the corrected same-expression/per-path E2 predicates and their negative fixtures bind the material console outcomes. |
| PR-9 Single-statement discipline | pass | Material events, sets, thresholds, paths, and review/handoff contracts are named once and referenced consistently; no materially divergent live spelling remains. |

#### create-plan §4A GUI Compliance

| Check | Result | Evidence |
|-------|--------|----------|
| Substitute control mapping | pass | With the three reference indexes absent, plan §4A maps all in-scope controls to test IDs, variants/sizes/states, feedback tiers, and E2E cases. |
| G30–G35 coverage | pass | Theme-aware `SelectInput`, unified accent/tokens, geometry-safe motion, canonical Button variants/sizes, and feedback tiers are explicit. |
| E2 written-and-wired proof | pass | Row 4 writes/wires the chrome wave and runs the corrected per-control/case census before Playwright; only a reproduced no-display run may be `[B]`. |
| G36 protection | pass | Vitest uses `--allowOnly=false`; the plan forbids test neutralization and scans unit/E2E skip/only/todo markers. |

### Non-Blocking Correction Note

- Materiality Gate applied: task row 6's anti-placeholder command scans the principal component/style directories but does not expand the named `SCAN_PLACEHOLDER_ARGS` across all of `ui/src`, so the modified hooks, registry, and router are outside that literal grep (`implementation-plan.md:111,146,151`; `task.md:49`). This is verification-scope maintenance, not a demonstrated material delivery false pass: TypeScript, Vitest, and the AC-specific gates still cover those behaviors. It does not block approval, but execution should use the named all-`ui/src` scope when producing the closeout receipt.

### Commands Executed

- Static redirected reads only: target/authority files, the current rolling review, the review template and peer exemplar, existing invoked E2E specs, and all census receipts.
- `Test-Path` receipts for the plan-local assertions, named helper owners, templates/schema/grouping authority, Zorivest local canon, and unstarted implementation artifacts.
- `rg` line-numbered reads/sweeps for plan/task consistency, corrected predicates, GUI canon/action-index terms, emerging standards, MEU registry, and E2E coverage.
- `--help` only for `tools/meu_status.py` (root/update/render), `tools/check_exec_review.py`, and `tools/export_openapi.py`.

No pytest, Vitest, Playwright, build, lint, typecheck, render, update, OpenAPI check/export, plan assertion script, or product mutation command was run.

### Open Questions / Assumptions

None requiring a product decision. The Human-approved MEU-26 insertion, right-side sheet, cyan/Dracula token choice, and default-closed behavior were treated as authoritative. Runtime Electron/display behavior remains execution-phase evidence.

### Follow-Up Action

No `/plan-corrections` action remains. This is the Round-3 cap review, and the review workflow stops here; implementation is outside this review pass.

### Verdict

`approved` — PR-6 passes, both Round-2 High findings are fixed, and no High/Critical delivery-level finding remains. The plan is executable as written for MEU-26 chrome only.

### Residual Risk

This was intentionally a static plan review. No project test or Electron runtime result is claimed. Execution must still produce the plan's Red/Green, Playwright or evidence-gated no-display receipt, scoped quality gate, handoff, and independent implementation-review evidence.
