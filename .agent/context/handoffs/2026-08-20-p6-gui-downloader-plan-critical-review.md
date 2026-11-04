---
date: "2026-08-20"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md"
verdict: "approved"
findings_count: 0
round: 5
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
---

# Critical Review: p6-gui-downloader

> **Review Mode**: `plan`
> **Verdict**: `changes_required`

---

## Scope

**Targets**: `docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md`; `docs/execution/plans/2026-08-20-p6-gui-downloader/task.md`  
**Review Type**: Round 1 plan review, static evidence only  
**Checklist Applied**: IR, DR-1–DR-8, PR-1–PR-9; Boundary Input Contract; control observable/call-chain/negative-oracle binding; PR-9 named sets; C2 Out of Scope; create-plan §4A GUI compliance  
**Scope Lock**: MEU-20 only. MEU-21–25, product implementation, tests, API rewrites, MCP rewrites, and plan corrections were excluded.

## Intent Anchor

Executing this plan is supposed to replace the Session 7 `SHELL_HOME` at `/` with the MEU-20 Downloader page, wire its form, queue, SABR, cookie, processor, command-palette, polling, and Electron E2E behavior to the already-approved MEU-15/19 surfaces, and stop before MEU-21–25. As written, the plan can complete with route-dependent palette actions and materially incomplete Red/E2E evidence, so it would not reliably deliver that objective.

---

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| 1 | High | High | **The global download palette controls terminate at a route-scoped consumer, so their production call chain is dead whenever `/` is not mounted.** `DOWNLOAD_EVENTS` makes `DownloaderPage` the only consumer, AC-20.13 traces palette → `CustomEvent` → `DownloaderPage`, and the Green task repeats that design. The current router proves `AppShell` is always mounted while `DownloaderPage` will own only `/`; the existing `/transcript`, `/tts`, and `/settings` routes therefore leave a palette-dispatched download event with no listener. This contradicts G11's always-mounted `AppShell` ownership and lacks the required negative oracle “invoke a download palette action off `/` and observe the same production effect.” This is a demonstrated PR-8 reachability failure, not a missing prose detail. | `implementation-plan.md:115,178,231,268-275`; `task.md:43`; `.agent/docs/emerging-standards.md:191-218`; `ui/src/renderer/src/router.tsx:21-54`; `ui/src/renderer/src/components/layout/AppShell.tsx:24-86` | Bind every palette-eligible download action to an always-mounted production owner (normally `AppShell`) or a source-backed navigate-and-deliver chain; add an off-route negative oracle and include the owner file in the change inventory/task. | open |
| 2 | High | High | **The Red gate can pass without the promised AC-20.1–20.22 test contract.** Row 1 runs the entire existing Vitest suite, then `assert-red-oracle.ps1` accepts any `FAIL`, `AssertionError`, or `Cannot find module`; neither surface proves that all 22 new AC tests exist, are collected, or fail for their intended missing behavior. A single superseded Session 7 assertion or unrelated failed test is enough to return `PASS: RED_ORACLE ui`, after which Green can proceed. Later handoff checks compare AC IDs in plan prose to handoff prose, not test files or collected test names. This permits a materially missing TDD deliverable and violates the FIC tests-first contract plus PR-4/PR-8. | `implementation-plan.md:58,143-144,215-240`; `task.md:42,45,55`; `assert-red-oracle.ps1:42-55`; `AGENTS.md:246-259` | Give the Red gate an exact AC/test inventory and expected failure oracle: prove every AC-20 test is present and collected, require the intended failed test names/assertions, and reject unrelated existing-suite failures before returning success. | open |
| 3 | High | High | **The §4A/E2 gate can pass while many new interactive controls have no Electron E2E assertion.** The page creates cookie radios/fields, Test Cookies, SABR Force/Clear, four reorder buttons, Reset, Remove, Clear All, and open-file/folder controls. The plan registers many of them only in `WAVE1_EXTRA_TESTIDS`; AC-20.16 requires six tests around `WAVE1_TESTIDS`, and task row 3 checks only six literal IDs plus file existence before running Playwright. It does not require test count, per-control presence/interactivity/visual assertions, or even the full 11-ID Wave 1 set. A six-test file that never touches the extra controls passes the exact task predicate, contrary to create-plan §4A item 3 and E2. | `implementation-plan.md:114-119,167-197,232-238,280-282`; `task.md:44`; `.agent/workflows/create-plan.md:245-264`; `.agent/docs/emerging-standards.md:1167-1186`; `docs/build-plan/06-gui.md:1091-1135` | Define the six Wave 1 test cases and their asserted controls explicitly; add a validation census that proves every new/modified interactive element is registered and referenced by a real Electron E2E assertion, including the extra controls. | open |
| 4 | Medium | High | **The §4A element map is incomplete for G34/G35.** Its `Variant / size` column gives variants but no sizes for most buttons, and it has no row/feedback tier for the planned open-file/open-folder actions. Inputs and status controls are grouped too broadly to prove each created element's canonical state mapping. Because the canonical GUI reference/index files are absent, this table is the only substituted mapping and must be complete. | `implementation-plan.md:114,167-197`; `.agent/workflows/create-plan.md:249-262`; `.agent/docs/emerging-standards.md:1132-1165` | Add every interactive element/action to the §4A table with an explicit canonical variant, size, states, testid, and feedback tier; state the local fallback basis while the reference indexes remain absent. | open |
| 5 | Medium | High | **Task H2-1 is not an exact receipt-producing validation.** Its validation cell is a `view_file:` placeholder and “latest peer reflection,” while its durable output is the unnamed phrase “Reflection source receipt.” There is no deterministic exemplar-selection rule, command, receipt path, or predicate that can be independently rerun. This fails IR validation exactness and PR-3/PR-4 even though the other task rows mostly use canonical redirected receipts. | `task.md:59`; `AGENTS.md:173-182` | Replace H2-1 with an exact read/selection command or deterministic read-tool procedure, name the receipt path, and validate template/schema/peer identities before H2-2. | open |
| 6 | Medium | High | **The plan does not schedule the Session 8 grouping authority to leave `planning` after execution.** It updates MEU SSOT, `docs/BUILD_PLAN.md`, current focus, reflection, and metrics, but omits `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` from the file inventory and every task row. Executing the plan therefore leaves the named Session 8 authority and its prerequisite-gate prose stale after MEU-20 becomes approved, violating DR-3/DR-6. | `implementation-plan.md:268-285,305-311`; `task.md:46,51,60-62`; `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md:19-21,184-193,276` | Add a post-approval grouping update with an exact static receipt that proves Session 8 is complete and Session 9 is the next allowed session, without starting MEU-21. | open |
| 7 | Medium | High | **`E2E_NO_LIVE_YT` is labeled `Human-approved` without a human approval reference, and its C2 basis is self-referential.** The context record has `human_message_reference: null`; the cited grouping says Session 8 started but does not approve this test restriction. The Out of Scope row cites only the plan-owned named set/lock. The restriction may be sensible, but its source classification is not auditable and it narrows the GUI shipping proof to Add/form oracles. This fails PR-5 and the C2 basis rule until it is tied to real canon/research or an actual user decision. | `implementation-plan.md:27-36,77,119,264,300`; `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md:184-193`; `docs/build-plan/06-gui.md:1124-1135` | Reclassify the rule with a real Local Canon/Research-backed source and define the non-live deterministic happy-path substitute, or obtain and cite explicit human approval. | open |
| 8 | Low | High | **The repeated `builder_model` literal is stale relative to the active harness profile.** Every active row names `cursor-grok-4.5-high-fast`, while the local profile records `cursor-grok-4.6-high`; `fresh_worker: none` makes this inert today, so it is clerical rather than blocking. The repeated live spelling also defeats PR-9's single-statement discipline. | `task.md:42-63`; `.agent/context/harness.local.md:19,26`; `PROJECT-PROFILE.md` Block F5 | Replace the repeated stale literal with one named current pin or `—` while `fresh_worker: none`, then reference that owner consistently. | open |

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | fail | AC-20.1–20.22 have labels, but the `Human-approved` classification for `E2E_NO_LIVE_YT` has no human approval reference (F7). |
| Validation cells are exact commands | fail | H2-1 has no exact command, receipt path, or deterministic peer selector (F5); Red and E2E commands are exact syntactically but materially false-pass their deliverables (F2–F3). |
| BUILD_PLAN audit row present | pass | Hub/SSOT binding and the next-session field have an exact redirected predicate (`implementation-plan.md:305-311`; `task.md:46`). |
| Post-MEU rows present (handoff, reflection, metrics) | pass | H1 handoff/review and H2 reflection/metrics/closeout rows are present and sequenced (`task.md:48-63`). |

### Documentation Review (DR-1–DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | All 18 actionable rows are `[ ]`; Downloader production/E2E/handoff/review artifacts are absent, matching an unstarted plan (`C:/Temp/av-kit/p6-review-not-started-and-target.txt`). |
| DR-2 Residual old terms | pass | `SHELL_HOME` and AC-19 references are explicitly marked as superseded inputs, not live ownership claims (`implementation-plan.md:71,87,150,219,235`). |
| DR-3 Downstream references updated | fail | The plan updates hub/SSOT/current-focus but omits the Session 8 grouping status transition (F6). |
| DR-4 Verification robustness | fail | Red and E2E predicates can pass with materially missing tests/assertions (F2–F3). |
| DR-5 Evidence auditability | fail | H2-1 lacks a named receipt and deterministic validation (F5). |
| DR-6 Cross-reference integrity | fail | The plan cites G11 while assigning the only download-event consumer to route-scoped `DownloaderPage` (F1); grouping would also remain stale (F6). |
| DR-7 Evidence freshness | pass | No implementation/test success is claimed; current existence/status counts were reproduced statically. |
| DR-8 Completion vs residual risk | pass | The targets remain draft/unstarted and do not claim implementation completion. |

### Plan Review (PR-1–PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | WP-20a→e aligns with task rows 1→5 and the H1→review→H2 ordering. |
| PR-2 Not-started confirmation | pass | Zero checked rows; Downloader source, Wave 1 E2E, MEU handoff, and implementation review are absent (`C:/Temp/av-kit/p6-review-not-started-and-target.txt`). |
| PR-3 Task contract completeness | fail | All rows have table cells, but H2-1 lacks an executable validation/receipt contract (F5). |
| PR-4 Validation realism | fail | The Red and E2E gates materially false-pass missing test deliverables; H2-1 is not independently runnable (F2, F3, F5). |
| PR-5 Source-backed planning | fail | The G11 implementation contradicts its cited standard, and `E2E_NO_LIVE_YT` is self-classified as Human-approved (F1, F7). |
| PR-6 Handoff/corrections readiness | pass | One MEU handoff and one rolling implementation-review path are explicit; Round 1 has no correction-census precondition. |
| PR-7 Scope discipline (C2) | fail | MEU-21–25 deferrals resolve correctly, but the live-YouTube out-of-scope row has a plan-owned/self-referential basis rather than a cited authority (F7). The named SSE/OCR/multi-file/MCP-Guard deferrals are substantively supported by `06-gui.md:1158-1167` and grouping line 59. |
| PR-8 Control reachability/totality | fail | Palette dispatch dead-ends off `/`; Red and E2E controls lack negative oracles that prove the promised test sets (F1–F3). Boundary request schemas otherwise match the existing `DownloadCreateIn`, `CookieTestIn`, `ReorderIn`, and `SettingsPutIn` surfaces. |
| PR-9 Single-statement discipline | fail | The core wire/status/control sets are named once, but the stale builder pin is repeated across task rows rather than owned once (F8); the materially incomplete E2E subset is covered by F3. |

---

## Commands Executed

- Read-only redirected reads of terminal preflight, the complete plan-review workflow, review template, harness/project context, role contracts, both targets, the latest approved peer review, and all named authorities.
- `C:/Temp/av-kit/p6-review-plan-1-200.txt`, `p6-review-plan-201-end.txt`, and `p6-review-task-all.txt` — line-numbered target copies.
- `C:/Temp/av-kit/p6-review-gui-palette.txt`, `p6-review-gui-downloader-a.txt`, `p6-review-gui-downloader-b.txt`, `p6-review-gui-e2e.txt`, `p6-review-session8.txt`, and `p6-review-gui-actions-all.txt` — build-plan/grouping/action authority.
- `C:/Temp/av-kit/p6-review-api-0.txt` through `p6-review-api-3.txt` — existing download/settings schemas and routes.
- `C:/Temp/av-kit/p6-review-ui-0.txt` through `p6-review-ui-3.txt` — current router/AppShell/registry/test-id topology.
- `C:/Temp/av-kit/p6-review-artifact-existence.txt` — referenced executable/artifact existence census.
- `C:/Temp/av-kit/p6-review-not-started-and-target.txt` — unstarted-state proof and canonical pre-edit guard.

No project tests, pytest, Vitest, Playwright, or `tools/` scripts were run. Evidence is static (`Get-Content`, `rg`, `Test-Path`) as required.

## Open Questions / Assumptions

- None requiring a new product decision. The blocking corrections can be resolved from G11, §4A/E2, the FIC/TDD contract, and the existing AppShell/API topology.
- This review treats the Session 7 `SHELL_HOME` assertions as intentionally superseded by Session 8, consistent with the grouping authority; it does not treat those test edits as G36 neutralization.

## Required Follow-Up

Apply `/plan-corrections` to F1–F8, produce the Round 1 blast-radius census required for a Round 2 resubmission, and keep all changes confined to the plan/task/plan-owned receipt helpers and necessary planning metadata. Do not begin MEU-20 implementation until a later independent review returns `approved`.

## Verdict

`changes_required` — three High findings demonstrate that executing the current plan can leave global download palette actions unreachable and can complete Red/E2E gates without the promised test contract. The plan therefore is not executable to the stated MEU-20 objective as written.

## Residual Risk

This was a static plan review. Runtime Electron behavior, actual request payloads, and sandbox display availability remain execution-phase risks; none were claimed as verified here. The existing FastAPI routes/schemas were read only and must not be rewritten by the correction pass.

## Corrections Applied (2026-08-20) — after Round 1

**Workflow**: `/plan-corrections` inside `/create-plan` §5b (parent loop wins over `plan-corrections.md` HARD STOP). Plan/task + plan-folder helper scripts only. No product code.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Conflict flagged**: `plan-corrections.md` Step 7 / HARD STOP say timestamp-and-stop and do not chain into re-review; `create-plan.md` §5b requires blast-radius census then re-dispatch. Parent create-plan loop is followed.

Round-1 findings 1–8 addressed. F1–F8 are `fixed` (none refuted).

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| 1 | High | fixed | `PALETTE_DELIVER` + `DOWNLOAD_COMMANDS`. `AppShell` always-mounted listener is the production owner. Off `/` uses `NAVIGATE_AND_DELIVER`. AC-20.13 negative: page-only listener / second fetch path. `PAGE_FILES` and Files Modified include `AppShell.tsx`. |
| 2 | High | fixed | `RED_AC_IDS` + `RED_TEST_TITLE`. `assert-red-oracle.ps1` ui kind requires all 22 `AC-20.N` ids (`AC-20.1` is not a substring match for `AC-20.10`). One unrelated FAIL is not enough. |
| 3 | High | fixed | `E2E_CASES` W1-1…W1-6 + `E2E_CONTROL_CENSUS` (`assert-e2e-control-census.ps1`). Task row 3 runs the census before Playwright. EXTRA now includes `open-file-btn` / `open-folder-btn`. |
| 4 | Medium | fixed | §4A table now has variant, size, states, testid, feedback per element, including open-file/open-folder. Local fallback basis is G34 text (indexes still absent). |
| 5 | Medium | fixed | H2-1 is an exact redirected receipt writing `REFLECTION_SOURCE_READ` via `REFLECTION_PEER_RULE`. |
| 6 | Medium | fixed | `GROUPING_FILE` + `GROUPING_DONE_MARK` scheduled at H2-2 after exec `approved`. Row 5 must not mark Session 8 complete. Sessions 9–12 stay pending. |
| 7 | Medium | fixed | `E2E_NO_LIVE_YT` reclassified Local Canon (Spec 549 + 06-gui 1129–1135). Substitute is `E2E_HAPPY_PATH` (`https://example.invalid/watch?v=e2e0001` → Add → `queue-row`). No Human-approved claim. |
| 8 | Low | fixed | `BUILDER_PIN` = `—` (`fresh_worker: none`). All task `builder_model` cells use that value once named. |

### Declared variants swept

Old: `only consumer`, `owned by page`, `view_file:`, `cursor-grok-4.5-high-fast`, `Human-approved (this plan lock 8)`, `this plan; no live YouTube`, `safety; Start not clicked`, `Reflection source receipt`.
New / semantic: `PALETTE_DELIVER`, `DOWNLOAD_COMMANDS`, `NAVIGATE_AND_DELIVER`, `RED_AC_IDS`, `RED_TEST_TITLE`, `E2E_CASES`, `E2E_HAPPY_PATH`, `E2E_CONTROL_CENSUS`, `BUILDER_PIN`, `GROUPING_DONE_MARK`, `GROUPING_FILE`, `REFLECTION_SOURCE_READ`, `open-file-btn`, `open-folder-btn`, `W1-1`, `example.invalid`, `AppShell`.

Manifest: `C:/Temp/av-kit/census-p6-dl-r1-manifest.txt`. Runner: `C:/Temp/av-kit/census-p6-dl-r1-run.txt`. Scripts exist: `assert-red-oracle.ps1`, `assert-e2e-control-census.ps1`, `assert-handoff-markers.ps1`.

Blast-radius census: 8 old + 17 new = 25 sweeps. Zero-hit old receipts: 8. Nonzero raw `file:line` hits: 73. Each hit dispositioned below. No truncated `Select-Object -First` / `head`.

### Zero-hit old receipts (stale gone)

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-dl-r1-only-consumer-old.txt` | 0 | no stale page-only consumer |
| `C:/Temp/av-kit/census-p6-dl-r1-owned-by-page-old.txt` | 0 | no stale G11 “owned by page” |
| `C:/Temp/av-kit/census-p6-dl-r1-view-file-old.txt` | 0 | no H2-1 `view_file:` placeholder |
| `C:/Temp/av-kit/census-p6-dl-r1-builder-45-old.txt` | 0 | no stale `cursor-grok-4.5-high-fast` |
| `C:/Temp/av-kit/census-p6-dl-r1-human-lock8-old.txt` | 0 | no lock-8 Human-approved claim |
| `C:/Temp/av-kit/census-p6-dl-r1-no-live-this-plan-old.txt` | 0 | no self-referential live-YT basis |
| `C:/Temp/av-kit/census-p6-dl-r1-safety-start-old.txt` | 0 | no unsourced “safety” sufficiency row |
| `C:/Temp/av-kit/census-p6-dl-r1-reflection-unnamed-old.txt` | 0 | no unnamed “Reflection source receipt” |

### Per-hit disposition — `PALETTE_DELIVER` (7)

Receipt: `C:/Temp/av-kit/census-p6-dl-r1-palette-deliver-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:45` | updated — Green row names the owner |
| 2 | `implementation-plan.md:59` | updated — WP-20b |
| 3 | `implementation-plan.md:117` | updated — named-set definition |
| 4 | `implementation-plan.md:121` | confirmed-consistent — W1-6 cites the set |
| 5 | `implementation-plan.md:192` | updated — §4A G11 row |
| 6 | `implementation-plan.md:261` | updated — AC-20.13 |
| 7 | `implementation-plan.md:304` | updated — Files Modified |

### Per-hit disposition — `DOWNLOAD_COMMANDS` (7)

Receipt: `C:/Temp/av-kit/census-p6-dl-r1-download-commands-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:45` | updated — Green row |
| 2 | `implementation-plan.md:59` | updated — WP-20b |
| 3 | `implementation-plan.md:116` | updated — named-set definition |
| 4 | `implementation-plan.md:117` | confirmed-consistent — used by `PALETTE_DELIVER` |
| 5 | `implementation-plan.md:192` | confirmed-consistent — §4A G11 |
| 6 | `implementation-plan.md:261` | confirmed-consistent — AC-20.13 |
| 7 | `implementation-plan.md:303` | updated — Files Modified |

### Per-hit disposition — `NAVIGATE_AND_DELIVER` (1)

Receipt: `C:/Temp/av-kit/census-p6-dl-r1-navigate-deliver-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:117` | confirmed-consistent — defined once inside `PALETTE_DELIVER`; AC-20.13 cites the parent set |

### Per-hit disposition — `RED_AC_IDS` (4) / `RED_TEST_TITLE` (3)

Receipts: `census-p6-dl-r1-red-ac-ids-new.txt`, `census-p6-dl-r1-red-test-title-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:44` | updated — Red row |
| 2 | `implementation-plan.md:58` | updated — WP-20a |
| 3 | `implementation-plan.md:125` | updated — `RED_AC_IDS` definition |
| 4 | `implementation-plan.md:157` | updated — `RED_ORACLE` requires the ids |
| 5 | `implementation-plan.md:126` | updated — `RED_TEST_TITLE` definition |

### Per-hit disposition — `E2E_CASES` (8) / `E2E_HAPPY_PATH` (8) / `E2E_CONTROL_CENSUS` (6)

Receipts: `census-p6-dl-r1-e2e-cases-new.txt`, `census-p6-dl-r1-e2e-happy-new.txt`, `census-p6-dl-r1-e2e-census-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | updated — row 3 names cases + happy path + census |
| 2 | `implementation-plan.md:60` | updated — WP-20c |
| 3 | `implementation-plan.md:77` | updated — lock 8 Local Canon + happy-path substitute |
| 4 | `implementation-plan.md:120–124` | updated — named-set definitions |
| 5 | `implementation-plan.md:189` | updated — §4A E2 row |
| 6 | `implementation-plan.md:264` | updated — AC-20.16 |
| 7 | `implementation-plan.md:294` | updated — sufficiency |
| 8 | `implementation-plan.md:313` | updated — Files Modified wave1 |
| 9 | `implementation-plan.md:316` | updated — assert scripts |
| 10 | `implementation-plan.md:332` | updated — C2 basis |

### Per-hit disposition — `BUILDER_PIN` (2)

Receipt: `C:/Temp/av-kit/census-p6-dl-r1-builder-pin-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:127` | updated — named-set definition |
| 2 | `task.md:38` | updated — table cells use the value `—` |

### Per-hit disposition — `GROUPING_DONE_MARK` (3) / `GROUPING_FILE` (4)

Receipts: `census-p6-dl-r1-grouping-done-new.txt`, `census-p6-dl-r1-grouping-file-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:48` | updated — row 5 forbids premature complete |
| 2 | `task.md:62` | updated — H2-2 applies + validates the mark |
| 3 | `implementation-plan.md:128–129` | updated — named-set definitions |
| 4 | `implementation-plan.md:315` | updated — Files Modified H2-only |

### Per-hit disposition — `REFLECTION_SOURCE_READ` (2)

Receipt: `C:/Temp/av-kit/census-p6-dl-r1-reflection-source-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:133` | updated — named-set definition |
| 2 | `task.md:61` | updated — H2-1 exact receipt |

### Per-hit disposition — `open-file-btn` / `open-folder-btn` (2+2)

Receipts: `census-p6-dl-r1-open-file-btn-new.txt`, `census-p6-dl-r1-open-folder-btn-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:119` | updated — `WAVE1_EXTRA_TESTIDS` |
| 2 | `implementation-plan.md:224–225` | updated — §4A rows |

### Per-hit disposition — `W1-1` (3) / `example.invalid` (1)

Receipts: `census-p6-dl-r1-w1-1-new.txt`, `census-p6-dl-r1-example-invalid-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | confirmed-consistent — cites `E2E_CASES` W1-1…W1-6 |
| 2 | `implementation-plan.md:121` | updated — case list owner |
| 3 | `implementation-plan.md:264` | confirmed-consistent — AC-20.16 cites the set |
| 4 | `implementation-plan.md:122` | confirmed-consistent — URL owned once by `E2E_HAPPY_PATH` |

### Per-hit disposition — `AppShell` (10)

Receipt: `C:/Temp/av-kit/census-p6-dl-r1-appshell-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:45` | updated — Green owner |
| 2 | `implementation-plan.md:59` | updated — WP-20b durable output |
| 3 | `implementation-plan.md:88` | updated — `PAGE_FILES` |
| 4 | `implementation-plan.md:117` | confirmed-consistent — `PALETTE_DELIVER` |
| 5 | `implementation-plan.md:161` | updated — `MEU20_TOUCHED` |
| 6 | `implementation-plan.md:174` | confirmed-consistent — G29 “AppShell YES” from MEU-19 (not the new listener) |
| 7 | `implementation-plan.md:192` | confirmed-consistent — §4A G11 |
| 8 | `implementation-plan.md:249` | confirmed-consistent — AC-20.1 outlet chain |
| 9 | `implementation-plan.md:261` | confirmed-consistent — AC-20.13 |
| 10 | `implementation-plan.md:304` | updated — Files Modified |

---

## Recheck (2026-08-20) — Round 2 of 3

**Workflow**: `/plan-critical-review` recheck after `/plan-corrections`  
**Agent**: `gpt-5.6-sol`  
**Review Mode**: `plan`  
**Verdict**: `changes_required`

### Scope

**Targets reviewed (read-only)**:

- `docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-e2e-control-census.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-handoff-markers.ps1`

**Checklist Applied**: IR; DR-1–DR-8; PR-1–PR-9; round-2 PR-6 pre-verdict gate; r1 F1–F8 adjudication; E2/G11/G15/G30–G36; MEU-20 scope lock.  
**Scope Lock**: MEU-20 only. MEU-21–25 were treated only as evidenced deferrals; no later-MEU deliverable was required and no MEU ID was invented.

### PR-6 Pre-Verdict Gate

`PASS`. The corrector named `C:/Temp/av-kit/census-p6-dl-r1-manifest.txt`; all 25 child receipts named by the manifest exist and were read. Excluding `[rtk]` banners, every manifest hit count equals its raw receipt count: eight old-term receipts have zero hits and the 17 new-term receipts contain 73 raw hit occurrences. Those occurrences resolve to 43 unique `implementation-plan.md|task.md:file:line` locations; the correction appendix dispositions cover all 43, including expanded ranges such as `implementation-plan.md:120–124`. Receipt: `C:/Temp/av-kit/pr6-disposition-coverage-r2.txt` (`MISSING=0`).

### Intent Anchor

Executing this plan is supposed to replace the Session 7 shell at `/` with a fully wired MEU-20 Downloader page and prove its queue, SABR, cookie, command-palette, polling, and Electron behavior against the already-approved MEU-15/19 surfaces, while stopping before MEU-21–25. The corrected plan fixes five prior findings, but its Red/E2E gates still permit materially missing tests and its proposed non-live Add happy path cannot create a queue row through the real backend; executing it would therefore not reliably deliver that objective.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| R2-1 | High | High | **R1 F2 remains open: `RED_ORACLE_CHECK` does not prove 22 distinct collected/failed AC tests.** The correction requires all 22 ID strings somewhere in the aggregate Vitest receipt, but it never counts distinct test cases or binds one failed test to one AC. A single failed test title containing `AC-20.1 AC-20.2 … AC-20.22` satisfies every regex and the generic `FAIL` marker while 21 promised AC tests are absent. That is a concrete false pass for a materially missing TDD deliverable, not regex-shape polish. | `implementation-plan.md:125-126,157-158`; `task.md:44`; `assert-red-oracle.ps1:44-71`; `AGENTS.md` §FIC-Based TDD | Validate a machine-readable Vitest inventory that proves 22 distinct collected tests mapped one-to-one to `RED_AC_IDS`, and bind their Red outcomes to the intended tests rather than aggregate receipt text. | still-open |
| R2-2 | High | High | **R1 F3 remains open: `E2E_CONTROL_CENSUS` treats textual occurrence as an E2E assertion.** For every control and case ID the script only runs `-notmatch` against raw file text. Comments/constants listing all WAVE1+EXTRA IDs plus six empty passing `test('W1-N', …)` bodies satisfy the census and Playwright command without any presence, interactivity, or visual-behavior assertion. E2 explicitly requires all three for every changed interactive element, so task row 3 can still complete with the material E2 deliverable missing. | `implementation-plan.md:118-124,189,264`; `task.md:46`; `assert-e2e-control-census.ps1:24-41`; `.agent/docs/emerging-standards.md:1167-1185` | Make the executable gate prove each ID is used by a real Playwright locator/expect/action contract and that the six named cases contain their required behavioral assertions; reject comments, registry-only literals, and empty tests. | still-open |
| R2-3 | High | High | **R1 F7 remains open and now has a demonstrated execution dead end: `E2E_HAPPY_PATH` cannot produce `queue-row` with `example.invalid` through the real Electron backend.** Electron spawns the production backend, production wiring constructs `YouTubeAdapter`, and `POST /downloads` calls `DownloadService.add_to_queue`, which calls real yt-dlp extraction before any row is created. The `.invalid` URL therefore errors before Add can yield a row, and the plan names no interception, fake adapter, or fixture seam. The cited Spec 549 / GUI shipping-gate lines require Add and a happy path; they do not state the `E2E_NO_LIVE_YT` prohibition, so the Local Canon classification and C2 basis are also unsupported. | `implementation-plan.md:77,122-123,264,294,332`; `ui/src/main/index.ts:160-197`; `packages/api/src/avkit_api/wiring.py:121-137`; `packages/api/src/avkit_api/routes/downloads.py:71-83`; `packages/core/src/avkit_core/services/download.py:166-183`; `packages/infrastructure/src/avkit_infra/youtube/adapter.py:380-406`; `docs/build-plan/06-gui.md:1129-1135` | Define an executable, source-backed deterministic E2E seam that lets real Electron exercise Add→row without rewriting the existing API schemas/routes (and separately preserves route-contract proof), or cite an authorized resolvable fixture. Reclassify the no-live restriction from a source that actually states it or remove it. | still-open |

### Round-1 Finding Adjudication

| R1 Finding | Prior Severity | Recheck Result | Evidence |
|------------|----------------|----------------|----------|
| F1 — route-scoped palette consumer | High | ✅ Fixed | `PALETTE_DELIVER` names `AppShell` as the always-mounted production owner, `DOWNLOAD_COMMANDS` as the single handler set, and an off-route negative oracle; AppShell is in the work package/task/file inventory (`implementation-plan.md:59,116-117,192,261,304`; `task.md:45`). |
| F2 — Red gate can pass without AC-20.1–20.22 tests | High | ❌ Still open | All ID strings are required, but distinct collected tests and per-test Red outcomes are not (`assert-red-oracle.ps1:58-71`; R2-1). |
| F3 — E2E gate can pass without interactive assertions | High | ❌ Still open | The new census is raw substring matching, not assertion/control-flow validation (`assert-e2e-control-census.ps1:24-41`; R2-2). |
| F4 — incomplete §4A element map | Medium | ✅ Fixed | The current table supplies explicit variant, size, states, testid, and feedback for the planned elements including open file/folder (`implementation-plan.md:198-227`). |
| F5 — H2-1 lacks deterministic receipt | Medium | ✅ Fixed | `REFLECTION_PEER_RULE` and `REFLECTION_SOURCE_READ` are named; task H2-1 selects a peer deterministically and writes a named redirected receipt (`implementation-plan.md:130-133`; `task.md:61`). |
| F6 — Session 8 grouping transition omitted | Medium | ✅ Fixed | `GROUPING_FILE` / `GROUPING_DONE_MARK` are scheduled only after execution approval and task H2-2 carries a static receipt (`implementation-plan.md:128-129,315`; `task.md:48,62`). |
| F7 — unsupported no-live classification | Medium | ❌ Still open (High material effect) | The replacement source does not state the restriction, and its proposed substitute cannot pass through the real Add call chain (`implementation-plan.md:77,122-123,332`; R2-3). |
| F8 — stale repeated builder pin | Low | ✅ Fixed | `BUILDER_PIN` is owned once as `—`; task rows use that value while `fresh_worker: none` (`implementation-plan.md:127`; `task.md:38,44-65`). |

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | fail | AC rows are labeled, but AC-20.16 incorporates `E2E_NO_LIVE_YT`, whose claimed Local Canon does not state that restriction (R2-3). |
| Validation cells are exact commands | fail | Commands are syntactically exact and redirected, but the Red/E2E predicates have demonstrated material false passes (R2-1, R2-2). H2-1 exactness is fixed. |
| BUILD_PLAN audit row present | pass | Plan audit and task row 5 bind MEU-20, preserve the prior plan slash, and set the next command (`implementation-plan.md:337-343`; `task.md:48`). |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows remain sequenced (`task.md:50-65`). |

#### Documentation Review (DR-1–DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | Static state remains unstarted: Downloader source, Wave 1 file, MEU handoff, and execution-review file are absent; MEU-20 remains pending. |
| DR-2 Residual old terms | pass | The eight declared stale variants have zero raw census hits; superseded Session 7 terms are labeled as replacement inputs. |
| DR-3 Downstream references updated | pass | Grouping transition is now explicitly H2-only after execution approval (F6 fixed). |
| DR-4 Verification robustness | fail | Red and E2E validation can false-pass materially missing tests; the happy-path fixture cannot reach a queue row (R2-1–R2-3). |
| DR-5 Evidence auditability | pass | PR-6 census, named receipts, deterministic H2-1 selection, and canonical helper paths are auditable. |
| DR-6 Cross-reference integrity | fail | `E2E_NO_LIVE_YT` is attributed to canon that mandates a happy path but does not state the restriction, and the substitute contradicts the production Add chain (R2-3). |
| DR-7 Evidence freshness | pass | All 25 PR-6 receipts were re-read; manifest counts reproduce exactly and disposition coverage is `MISSING=0`. |
| DR-8 Completion vs residual risk | pass | Plan remains draft/unstarted and makes no implementation-complete claim. |

#### Plan Review (PR-1–PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | WP-20a–e aligns with task rows 1–5 and H1→review→H2 ordering; both carry the same corrected controls. |
| PR-2 Not-started confirmation | pass | Product/E2E/handoff/review deliverables are absent and actionable task rows remain unchecked. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, validation, dependency, strategy, durable output, builder pin, and status cells. |
| PR-4 Validation realism | fail | R2-1 and R2-2 demonstrate concrete false passes; R2-3 demonstrates an impossible Add→row fixture. |
| PR-5 Source-backed planning | fail | The no-live rule is not stated by its cited Local Canon (R2-3). Other ACs and boundary rules resolve to the named specs/schemas. |
| PR-6 Handoff/corrections readiness | pass | Manifest + all child receipts + per-hit dispositions are complete and mutually auditable (`C:/Temp/av-kit/pr6-disposition-coverage-r2.txt`). |
| PR-7 Scope discipline (C2) | fail | MEU-21–25 deferrals are valid and no IDs were invented, but the live-YouTube out-of-scope row cites sources that do not omit/prohibit the activity and its substitute is non-executable (R2-3). |
| PR-8 Control reachability/totality | fail | Palette reachability is fixed, but the Red/E2E validation observables remain vacuous and the E2E happy-path call chain dead-ends at real extraction (R2-1–R2-3). |
| PR-9 Single-statement discipline | pass | Corrected control sets, builder pin, grouping marks, and receipt owners are defined once and referenced by name; no materially divergent live spelling remains. |

### Commands Executed

- Static redirected reads only (`Get-Content`, `rg`, `Test-Path`, `Select-String`); no project tests, pytest, Vitest, Playwright, or `tools/` scripts were executed.
- `C:/Temp/av-kit/pr6-review-manifest-r2.txt` — round-1 correction appendix and manifest.
- `C:/Temp/av-kit/pr6-all-children-r2.txt` — all 25 child receipts with raw non-banner counts.
- `C:/Temp/av-kit/pr6-disposition-coverage-r2.txt` — 43/43 unique raw locations dispositioned.
- `C:/Temp/av-kit/p6-plan-r2-1-190.txt`, `p6-plan-r2-191-end.txt`, and `p6-task-scripts-r2.txt` — current review targets with stable line numbers.
- `C:/Temp/av-kit/p6-authority-gui-r2.txt`, `p6-existing-contracts-r2.txt`, `p6-rules-scope-r2.txt`, and `p6-e2-g35-g36-r2.txt` — canonical GUI/API/schema/grouping/MEU/standard evidence.
- `C:/Temp/av-kit/p6-real-backend-chain-r2.txt` — Electron→production backend→YouTube extraction chain.
- `C:/Temp/av-kit/p6-static-sweeps-preedit-r2c.txt` — target existence, canonical pre-edit guard, unstarted artifacts, tool existence, MEU scope, and invented-ID census.

### Open Questions / Assumptions

- No human product decision is required to understand the blockers. The next correction must choose and source a deterministic E2E seam because the current plan simultaneously forbids live extraction and requires a row created through an endpoint that extracts before persistence.
- This review treats the absence of product/E2E/handoff artifacts as not-started evidence and does not infer implementation from plan-owned helper scripts or correction receipts.

### Required Follow-Up

Apply `/plan-corrections` to R2-1–R2-3 only, keep changes within the MEU-20 plan/task/plan-owned static helpers and any source-backed planning metadata, and produce the round-2 blast-radius census required for round 3. Do not begin MEU-20 implementation unless round 3 returns `approved`.

### Verdict

`changes_required` — three High-confidence, High-severity findings demonstrate that the plan can complete without the promised Red/E2E test contract and that its specified Add→row happy path cannot execute through the real backend. Five of eight round-1 findings are fixed; F2, F3, and F7 remain open.

### Residual Risk

This was a static plan recheck. Runtime Electron behavior, display availability, external yt-dlp behavior, and actual test implementation remain execution-phase risks and were not claimed as verified. The existing `packages/api/` routes/schemas were read only and remain outside the correction scope.

## Corrections Applied (2026-08-20) — after Round 2

**Workflow**: `/plan-corrections` inside `/create-plan` §5b. Plan/task + plan-folder helper scripts only. No product code.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Conflict flagged**: parent create-plan loop re-dispatches; `plan-corrections.md` HARD STOP is not followed.

Round-2 findings R2-1–R2-3 addressed. All three are `fixed` (none refuted).

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| R2-1 | High | fixed | `RED_JSON` (Vitest 3 `--reporter=json`). `assert-red-oracle.ps1` requires `-JsonReceipt` and maps 22 distinct failed `assertionResults` 1:1 onto `RED_AC_IDS`. A title containing more than one AC id fails. |
| R2-2 | High | fixed | `E2E_LOCATOR_FORM` = literal `getByTestId('<id>')`. Census comment-strips, requires per-case `expect` + visual/interact markers, and rejects empty/skip tests. W1-3/W1-5 bind EXTRA + enabled/disabled. |
| R2-3 | High | fixed | `E2E_SEAM` = Playwright `page.route` (research-backed). No-live basis is Local Canon `download.py` 166–175 extract-before-persist, not Spec 549. `E2E_HAPPY_PATH` Add→row runs only through the seam. |

### Declared variants swept

Old: `one unrelated FAIL`, `all 22 AC ids collected`, `Local Canon: Spec 549 + 06-gui 1129–1135`, `Enforced by Spec 549`.
New / semantic: `RED_JSON`, `JsonReceipt`, `assertionResults`, `E2E_SEAM`, `E2E_LOCATOR_FORM`, `page.route`, `download.py` 166, `fail-to-pass-meu-20-ui.json`, `getByTestId('<kebab-id>')`, `multi-id`.

Manifest: `C:/Temp/av-kit/census-p6-dl-r2-manifest.txt`. Runner: `C:/Temp/av-kit/census-p6-dl-r2-run.txt`.

Blast-radius census: 4 old + 10 new = 14 sweeps. Zero-hit old receipts: 4. Nonzero raw hits: 40. Each hit dispositioned below. No truncation.

### Zero-hit old receipts

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-dl-r2-unrelated-fail-old.txt` | 0 | no stale “one unrelated FAIL” |
| `C:/Temp/av-kit/census-p6-dl-r2-all-22-collected-old.txt` | 0 | no substring-only “22 AC ids collected” |
| `C:/Temp/av-kit/census-p6-dl-r2-nolive-spec549-old.txt` | 0 | no Spec-549-as-no-live Local Canon |
| `C:/Temp/av-kit/census-p6-dl-r2-nolive-spec549-short-old.txt` | 0 | no “Enforced by Spec 549” |

### Per-hit disposition — `RED_JSON` / `JsonReceipt` / `assertionResults` / json path / `multi-id`

Receipts: `census-p6-dl-r2-red-json-new.txt`, `json-receipt-new.txt`, `assertion-results-new.txt`, `red-json-path-new.txt`, `stuffed-title-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:44` | updated — Red row writes `RED_JSON` and passes `-JsonReceipt` |
| 2 | `implementation-plan.md:58` | updated — WP-20a |
| 3 | `implementation-plan.md:127` | updated — `RED_AC_IDS` owner includes JSON |
| 4 | `implementation-plan.md:128` | updated — `RED_TEST_TITLE` forbids multi-id titles |
| 5 | `implementation-plan.md:129` | updated — `RED_JSON` definition |
| 6 | `implementation-plan.md:160–161` | updated — `RED_ORACLE` / `RED_ORACLE_CHECK` |

### Per-hit disposition — `E2E_SEAM` / `page.route` / `download.py` 166

Receipts: `census-p6-dl-r2-e2e-seam-new.txt`, `page-route-new.txt`, `download-py-166-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | updated — row 3 names seam |
| 2 | `implementation-plan.md:77` | updated — lock 8 |
| 3 | `implementation-plan.md:121` | updated — W1-4 via seam |
| 4 | `implementation-plan.md:123–125` | updated — named-set definitions |
| 5 | `implementation-plan.md:267` | updated — AC-20.16 |
| 6 | `implementation-plan.md:297` | updated — sufficiency |
| 7 | `implementation-plan.md:316–317` | updated — Files Modified |
| 8 | `implementation-plan.md:336` | updated — C2 basis |
| 9 | `implementation-plan.md:410` | updated — research reference |

### Per-hit disposition — `E2E_LOCATOR_FORM` / `getByTestId('<kebab-id>')`

Receipts: `census-p6-dl-r2-locator-form-new.txt`, `getByTestId-form-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | updated — row 3 |
| 2 | `implementation-plan.md:122` | updated — named-set definition |
| 3 | `implementation-plan.md:126` | updated — census owner cites the form |

---

## Recheck (2026-08-20) — Round 3 of 3 (Plan-Review Cap)

**Workflow**: `/plan-critical-review` recheck after the second `/plan-corrections` pass  
**Agent**: `gpt-5.6-sol`  
**Review Mode**: `plan`  
**Verdict**: `changes_required`

### Scope

**Targets reviewed (read-only)**:

- `docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-e2e-control-census.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-handoff-markers.ps1`

**Checklist Applied**: IR; DR-1–DR-8; PR-1–PR-9; round-3 PR-6 pre-verdict gate; R2-1–R2-3 adjudication; G5/G11/G15/G30–G36/E2/UX2; MEU-20 scope lock.  
**Scope Lock**: MEU-20 only. MEU-21–25 were considered only as registered, evidence-backed deferrals. No later-MEU deliverable was required and no MEU ID was invented.

### PR-6 Pre-Verdict Gate

`PASS`. The after-Round-2 correction appendix names `C:/Temp/av-kit/census-p6-dl-r2-manifest.txt`; the manifest and every one of its 14 child receipts were read. Excluding `[rtk]` banners and blank lines, the four old-term receipts contain zero hits and the ten positive receipts contain exactly the declared 40 raw hits. Every unique raw `file:line` location is covered by an `updated` disposition in the appendix, including the declared ranges `implementation-plan.md:123–125`, `implementation-plan.md:160–161`, and `implementation-plan.md:316–317`. `C:/Temp/av-kit/review-r3-pr6-count-audit.txt` records `PR6_COUNT_MISMATCHES=0` and `PASS: PR6_CHILD_COUNTS`.

### Intent Anchor

Executing this plan is supposed to replace the Session 7 shell at `/` with the complete MEU-20 Downloader page, prove its queue, SABR, cookie, palette, polling, and Electron behavior against the approved MEU-15/19 surfaces, and stop before MEU-21–25. The second correction pass fixes the Red inventory and deterministic Add seam, but the E2E control census can still approve a materially incomplete Wave 1 suite, so executing the plan would not reliably deliver that objective.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| R3-1 (R2-2) | High | High | **The E2E gate still permits most new controls to have no behavioral assertion.** The correction now strips comments, requires literal locators, and rejects empty cases, but W1-3 only proves that all 24 EXTRA/SABR locators occur somewhere in its block and then accepts one visual matcher anywhere in that block. W1-5 likewise requires 13 control locators but accepts one enabled/disabled matcher anywhere. A test can therefore mention every required control, assert only one control in each case, and pass `E2E_CONTROL_CENSUS`. That is the same material R2-2 false pass: E2 requires each changed interactive element's presence, interactivity, and visual behavior to be asserted, while task row 3 treats this helper as the precondition for completion. | `implementation-plan.md:121-126,192-193,267`; `task.md:46`; `assert-e2e-control-census.ps1:88-113`; `.agent/docs/emerging-standards.md:1167-1185` | Bind every required control to its own applicable Playwright assertion/action contract (for example, per-ID presence assertions in W1-3 and per-ID enabled/disabled assertions in W1-5), or validate a machine-readable per-control oracle that the runtime test consumes. A block-level “at least one matcher” predicate is insufficient. | still-open |

### Round-2 Finding Adjudication

| Round-2 Finding | Prior Severity | Recheck Result | Evidence |
|-----------------|----------------|----------------|----------|
| R2-1 — Red gate can pass without 22 distinct failed AC tests | High | ✅ Fixed | The UI oracle now requires a Vitest JSON receipt, enumerates `testResults[].assertionResults[]`, rejects multi-ID titles, requires exactly one assertion record per AC-20.1–20.22, and requires every mapped record to be failed (`assert-red-oracle.ps1:59-115`; `task.md:44`). |
| R2-2 — E2E census treats occurrence as assertion | High | ❌ Still open | Comment/empty-test bypasses are fixed, but the helper still checks locator membership per block plus only one matcher for the whole multi-control block; it does not bind each control to an assertion (`assert-e2e-control-census.ps1:88-113`; R3-1). |
| R2-3 — non-live Add happy path dead-ends before persistence | High | ✅ Fixed | `apiFetch` uses renderer `fetch`, which Playwright `page.route()` can intercept; the plan now defines `E2E_SEAM`, request-body checking, fixtures, and Add→row through the seam. The real service still extracts before persistence, so the seam removes the original dead end without changing API code (`implementation-plan.md:77,123-125,267,297`; `ui/src/renderer/src/lib/api.ts:19-29`; `packages/core/src/avkit_core/services/download.py:166-175`; Playwright Network documentation). |

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-20.1–20.22 are labeled to Spec, Local Canon, Research-backed sources, boundary canon, or explicit review locks; the E2E seam combines the real extract-before-persist call chain with official Playwright routing capability. |
| Validation cells are exact commands | fail | Commands and receipt paths are exact, but task row 3's executable census has the demonstrated R3-1 material false pass. |
| BUILD_PLAN audit row present | pass | Task row 5 binds MEU-20, preserves the prior phase-6 plan slash, and sets the next command without starting MEU-21 (`implementation-plan.md:341-347`; `task.md:48`). |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows are present and ordered (`task.md:50-65`). |

#### Documentation Review (DR-1–DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | fail | The after-Round-2 appendix claims R2-2 fixed, but the current helper retains the block-level one-matcher false pass (R3-1). R2-1 and R2-3 claims match current state. |
| DR-2 Residual old terms | pass | All four declared stale-term receipts contain zero non-banner hits. |
| DR-3 Downstream references updated | pass | Grouping transition is scheduled only after execution approval; hub/SSOT/current-focus surfaces are accounted for. |
| DR-4 Verification robustness | fail | `E2E_CONTROL_CENSUS` can pass with most controls unasserted (R3-1). |
| DR-5 Evidence auditability | pass | PR-6 manifest/children/dispositions, plan-owned helpers, and named receipts are reproducible. |
| DR-6 Cross-reference integrity | pass | MEU-20 scope, AppShell ownership, renderer fetch, API schemas/routes, and extract-before-persist seam are mutually traceable without API/MCP rewrites. |
| DR-7 Evidence freshness | pass | All 14 current round-2 census children were re-read; declared and actual non-banner counts match exactly. |
| DR-8 Completion vs residual risk | pass | The plan remains unstarted and does not claim implementation completion. |

#### Plan Review (PR-1–PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | WP-20a–e aligns with task rows 1–5 and the H1→review→H2 sequence; both surfaces carry the same named controls. |
| PR-2 Not-started confirmation | pass | Nineteen task rows remain unchecked; Downloader production, Wave 1 E2E, MEU handoff, and implementation-review artifacts are absent (`C:/Temp/av-kit/review-r3-unstarted.txt`). |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, validation, dependency, context strategy, durable output, builder pin, and status. |
| PR-4 Validation realism | fail | R3-1 demonstrates that task row 3 can complete while a material E2 deliverable is absent. |
| PR-5 Source-backed planning | pass | Product behavior and planning-only seam rules resolve to the named spec, existing schemas/routes/service, emerging standards, grouping authority, or official Playwright documentation. |
| PR-6 Handoff/corrections readiness | pass | Manifest, 14 children, exact counts, and per-location dispositions are complete; one rolling MEU handoff and review path remain explicit. |
| PR-7 Scope discipline (C2) | pass | MEU-21–25 exist in `meu-status.yaml` and are valid deferral targets; remaining out-of-scope rows cite sources that omit or assign the work elsewhere. |
| PR-8 Control reachability/totality | fail | Palette reachability, Red mapping, and the renderer fetch seam are now bound, but the E2 census observable does not prove each control's asserted behavior (R3-1). |
| PR-9 Single-statement discipline | pass | Repeated behavioral sets are named and referenced; executable helper literals are their enforcement surfaces, with no materially divergent live spelling found. |

### Non-Blocking Correction Note

- The `E2E_SEAM` prose says the POST handler fulfills `{ items, processor }`, while the existing `DownloadCreateOut` response is `{ items }` and only `GET /downloads` returns `{ items, processor }` (`implementation-plan.md:123`; `packages/api/src/avkit_api/schemas/downloads.py:66-76`; `packages/api/src/avkit_api/routes/downloads.py:71-93`). Preserve the route-specific envelopes when implementing fixtures. Under the Materiality Gate this is a clerical correction: the seam remains reachable and an intelligent reader can infer the two existing response shapes.

### Commands Executed

- Static redirected reads only (`Get-Content`, `rg`, `Test-Path`, `Resolve-Path`); no project tests, pytest, Vitest, Playwright, or validation scripts were run.
- `C:/Temp/av-kit/review-r3-census-manifest-numbered.txt` and `review-r3-census-children-raw.txt` — manifest plus every child receipt.
- `C:/Temp/av-kit/review-r3-pr6-count-audit.txt` — exact child-count reproduction (`PR6_COUNT_MISMATCHES=0`).
- `C:/Temp/av-kit/review-r3-plan-1-220.txt`, `review-r3-plan-221-end.txt`, `review-r3-task-only.txt`, and `review-r3-scripts.txt` — line-numbered targets.
- `C:/Temp/av-kit/review-r3-gui-1091-1135.txt`, `review-r3-gui-actions.txt`, `review-r3-session8-exact.txt`, `review-r3-emerging-standards.txt`, and `review-r3-existing-contracts.txt` — named authority and current contract evidence.
- `C:/Temp/av-kit/review-r3-unstarted.txt`, `review-r3-meu-scope.txt`, and `review-r3-pre-edit-guard.txt` — unstarted state, registered deferrals, and canonical write-target proof.
- Official Playwright Network documentation was read to confirm that `page.route()` can handle page `fetch` requests.

### Open Questions / Assumptions

- No product decision is needed to understand R3-1; it is an executable predicate defect against E2's existing per-element contract.
- Runtime Electron behavior, display availability, and the eventual route glob implementation remain execution-phase risks; no runtime result is claimed here.

### Required Human Decision — Plan-Review Cap Reached

This is round 3 of 3 and the verdict is not `approved`. Per the workflow cap, do not begin MEU-20 execution and do not auto-run another correction/review round. Human direction is required to choose whether to authorize a cap exception after correcting R3-1, explicitly waive or revise the E2 per-control gate, or stop this plan.

### Verdict

`changes_required` — one High-confidence, High-severity finding remains. The plan's E2E gate can still pass while most new controls have no behavioral assertion, so the plan is not executable to the stated MEU-20 objective as written. The plan-review cap is reached.

### Residual Risk

This was a static plan recheck. No project tests were run. The route-specific fixture-envelope note is non-blocking, but should be corrected during any human-authorized revision. Runtime Electron/display behavior remains unverified and belongs to execution.

## Corrections Applied (2026-08-20) — after Round 3 (human cap exception)

**Workflow**: `/plan-corrections` inside `/create-plan` §5b. USER_EXPLICIT 2026-08-20: “continue review until approved” — authorizes one more review round past the plan-review cap of 3.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Write scope**: plan/task + `assert-e2e-control-census.ps1` only.

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| R3-1 | High | fixed | `E2E_PER_CONTROL`: each required id must have `getByTestId('id')` bound to its own assertion/action before the next `getByTestId`. W1-3 per-id visual; W1-5 per-id enabled/disabled; W1-4 fill/click/visible; W1-1/W1-6 per-id visible/focused. Block-level one-matcher is a fail. |
| r3 clerical | Low | fixed | `E2E_SEAM` POST fulfills `DownloadCreateOut` `{ items }`; GET fulfills `LIST_ENVELOPE` `{ items, processor }`. |

### Declared variants swept

Old: `fulfills `{ items, processor }` with one Pending row`.
New / semantic: `E2E_PER_CONTROL`, `DownloadCreateOut`, `bound assertion`, `before the next getByTestId`.
Keep (prohibition, not stale gate): `one matcher per block` in task.md:46.

Manifest: `C:/Temp/av-kit/census-p6-dl-r3-manifest.txt`. Runner: `C:/Temp/av-kit/census-p6-dl-r3-run.txt`.

Blast-radius census: 2 old + 4 new = 6 sweeps. Zero-hit stale POST-envelope: 1. Nonzero raw hits: 13. Each dispositioned below. No truncation.

### Zero-hit old receipts

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-dl-r3-fulfills-list-on-post-old.txt` | 0 | no POST-as-list-envelope leftover |

### Per-hit disposition — `one matcher per block` (1)

Receipt: `C:/Temp/av-kit/census-p6-dl-r3-one-matcher-old.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | confirmed-consistent — names the forbidden false-pass, not the live gate |

### Per-hit disposition — `E2E_PER_CONTROL` (6)

Receipt: `C:/Temp/av-kit/census-p6-dl-r3-per-control-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | updated — row 3 |
| 2 | `implementation-plan.md:60` | updated — WP-20c |
| 3 | `implementation-plan.md:123` | updated — named-set definition |
| 4 | `implementation-plan.md:127` | updated — census owner |
| 5 | `implementation-plan.md:193` | updated — §4A E2 |
| 6 | `implementation-plan.md:268` | updated — AC-20.16 |

### Per-hit disposition — `DownloadCreateOut` (2)

Receipt: `C:/Temp/av-kit/census-p6-dl-r3-download-create-out-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:124` | updated — `E2E_SEAM` POST envelope |
| 2 | `implementation-plan.md:273` | confirmed-consistent — existing AC-20.21 |

### Per-hit disposition — `bound assertion` (3) / `before the next getByTestId` (1)

Receipts: `census-p6-dl-r3-bound-assertion-new.txt`, `before-next-getByTestId-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | updated — row 3 |
| 2 | `implementation-plan.md:123` | updated — `E2E_PER_CONTROL` |
| 3 | `implementation-plan.md:127` | updated — census |
| 4 | `implementation-plan.md:268` | updated — AC-20.16 negative |

---

## Recheck (2026-08-20) — Round 4 (Human Cap Exception)

**Workflow**: `/plan-critical-review` recheck after the Round-3 `/plan-corrections` pass  
**Agent**: `gpt-5.6-sol`  
**Review Mode**: `plan`  
**Verdict**: `changes_required`  
**Cap authority**: `USER_EXPLICIT` 2026-08-20 — “continue review until approved.”

### Scope

**Targets reviewed (read-only)**:

- `docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-e2e-control-census.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-handoff-markers.ps1`

**Checklist Applied**: IR; DR-1–DR-8; PR-1–PR-9; round-4 PR-6 pre-verdict gate; R3-1 and the Round-3 envelope note; G11/G30–G36/E2; MEU-20 scope lock.  
**Scope Lock**: MEU-20 only. MEU-21–25 were checked only as registered, evidence-backed deferrals; no later-MEU deliverable was required and no MEU ID was invented.

### PR-6 Pre-Verdict Gate

`PASS`. The after-Round-3 correction appendix names `C:/Temp/av-kit/census-p6-dl-r3-manifest.txt`. The manifest and all six child receipts were read. Excluding `[rtk]` banners and blank lines, the declared/actual raw-hit counts are exactly `1, 0, 6, 2, 3, 1` (`PR6_COUNT_MISMATCHES=0`), totaling 13 nonzero raw `file:line` hits. The appendix dispositioned every hit as `updated` or `confirmed-consistent`: one `one matcher per block` hit, six `E2E_PER_CONTROL` hits, two `DownloadCreateOut` hits, three `bound assertion` hits, and one `before the next getByTestId` hit (`review-r4-pr6-count-audit.txt`; correction appendix lines 590–656).

### Intent Anchor

Executing this plan is supposed to replace the Session 7 shell at `/` with the complete MEU-20 Downloader page, prove its queue, SABR, cookie, palette, polling, and Electron behavior against the approved MEU-15/19 surfaces, and stop before MEU-21–25. The POST/GET fixture envelopes are now correct, but the corrected E2E census still admits a materially incomplete Wave 1 suite, so executing the plan would not reliably deliver that objective.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|----------|------------|---------|-----------|----------------|--------|
| R4-1 (R3-1 / R2-2) | High | High | **`Assert-HasBound` still proves proximity, not that the required control is the assertion/action target.** Its regex accepts any allowed method within 120 characters after `getByTestId('<required-id>')`, provided no later `getByTestId` occurs first. For example, `page.getByTestId('quality-select'); await expect(unrelatedLocator).toBeVisible();` satisfies the `quality-select` check even though no assertion targets that control; repeating the pattern before each next locator lets W1-3 or W1-5 pass while every required control remains behaviorally unasserted. This is the same material R3-1 false pass against E2's per-element presence/interactivity/visual contract, and task row 3 treats the helper as a completion precondition. | `assert-e2e-control-census.ps1:22-27,84-104`; `implementation-plan.md:123,127,193,268`; `task.md:46`; `.agent/docs/emerging-standards.md:1167-1185` | Require the allowed assertion/action to consume the required locator expression itself (for example, exact `expect(page.getByTestId('id')).toBeVisible()` / `page.getByTestId('id').click()` forms), or validate an AST/machine-readable per-control oracle. A nearby method on an unrelated receiver must fail. | still-open |

### Round-3 Adjudication

| Round-3 Item | Prior Status | Recheck Result | Evidence |
|--------------|--------------|----------------|----------|
| R3-1 — per-control E2E census | open High | ❌ Still open | The helper iterates each ID, but `Assert-HasBound` does not bind the matched method to that locator; the concrete unrelated-receiver sequence above passes its regex (`assert-e2e-control-census.ps1:22-27`). |
| POST vs GET `E2E_SEAM` envelopes | clerical correction note | ✅ Fixed | The plan now assigns POST `/downloads` to `DownloadCreateOut { items }` and GET `/downloads` to `LIST_ENVELOPE { items, processor }`, matching build-plan routes and current schema/router state (`implementation-plan.md:124`; `04-rest-api.md:152-172`; `schemas/downloads.py:66-76`; `routes/downloads.py:71-92`). |

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-20.1–20.22 remain sourced to Spec, Local Canon, Research-backed material, boundary canon, or explicit plan locks. |
| Validation cells are exact commands | fail | Commands and receipt paths are exact, but task row 3's executable census retains the demonstrated R4-1 material false pass. |
| BUILD_PLAN audit row present | pass | Task row 5 binds MEU-20, preserves the prior phase-6 plan slash, and updates the next command without starting MEU-21. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows remain present and correctly ordered (`task.md:50-65`). |

#### Documentation Review (DR-1–DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | fail | The Round-3 appendix claims R3-1 fixed, but the current helper proves only method proximity, not receiver binding (R4-1). Its POST/GET envelope claim does match current state. |
| DR-2 Residual old terms | pass | The one retained `one matcher per block` hit is an explicit prohibition; the stale POST-as-list-envelope receipt has zero non-banner hits. |
| DR-3 Downstream references updated | pass | Grouping completion remains scheduled only after execution approval; hub, SSOT, current-focus, and closeout surfaces are accounted for. |
| DR-4 Verification robustness | fail | `E2E_CONTROL_CENSUS` can pass when allowed methods operate on unrelated receivers (R4-1). |
| DR-5 Evidence auditability | pass | The PR-6 manifest, all children, per-hit dispositions, plan-owned helpers, and named receipts are reproducible. |
| DR-6 Cross-reference integrity | pass | MEU-20 scope, AppShell ownership, REST envelopes, and extract-before-persist seam are mutually consistent without API/MCP rewrites. |
| DR-7 Evidence freshness | pass | All six current Round-3 census children were re-read; declared and actual non-banner counts match exactly. |
| DR-8 Completion vs residual risk | pass | All 18 actionable task rows remain unchecked and no Downloader implementation, MEU handoff, or implementation-review artifact exists. |

#### Plan Review (PR-1–PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | WP-20a–e aligns with task rows 1–5 and the H1→review→H2 sequence; the corrected named controls are carried consistently. |
| PR-2 Not-started confirmation | pass | All 18 actionable rows are `[ ]`; `DownloaderPage.tsx`, `download-queue.test.ts`, the MEU-20 handoff, and the implementation-review file are absent (`review-r4-static-state.txt`; `review-r4-task-contract.txt`). |
| PR-3 Task contract completeness | pass | All 18 actionable rows have nonempty owner, deliverable, validation, dependency/context/durable-output fields, and status (`INCOMPLETE_CONTRACT_ROWS=0`). |
| PR-4 Validation realism | fail | R4-1 demonstrates that task row 3 can complete while a material E2 deliverable is absent. |
| PR-5 Source-backed planning | pass | Product behavior and seam rules resolve to the named build-plan, existing schemas/routes/service, emerging standards, grouping authority, or cited primary documentation. |
| PR-6 Handoff/corrections readiness | pass | Manifest, six children, exact counts, and all 13 per-hit dispositions are complete; the one rolling MEU handoff and review paths remain explicit. |
| PR-7 Scope discipline (C2) | pass | MEU-21–25 are registered in `meu-status.yaml` and the grouping file; remaining out-of-scope rows cite sources assigning or omitting the work. |
| PR-8 Control reachability/totality | fail | REST and AppShell chains are reachable, but the E2 census observable does not prove the asserted method consumes each required control locator (R4-1). |
| PR-9 Single-statement discipline | pass | Behavioral sets remain named and referenced; no materially divergent live spelling was found in the corrected surfaces. |

### Non-Blocking Correction Notes

None. The prior route-envelope note is fixed.

### Commands Executed

- Static redirected reads only (`Get-Content`, `rg`, `Test-Path`, and PowerShell receipt/count inspection); no project tests, pytest, Vitest, Playwright, or plan assertion scripts were run.
- `C:/Temp/av-kit/pr6-manifest-read-r4.txt`, `pr6-child-receipts-r4.txt`, and `review-r4-pr6-count-audit.txt` — manifest, all child receipts, and exact non-banner count audit.
- `C:/Temp/av-kit/plan-r4-*.txt`, `task-r4.txt`, `red-oracle-r4.txt`, `e2e-census-script-r4.txt`, and `handoff-markers-r4.txt` — line-numbered review targets.
- `C:/Temp/av-kit/gui-authority-r4.txt`, `rest-download-authority-r4.txt`, `g11-r4.txt`, `g30-e2-g36-r4.txt`, and `download-service-authority-r4.txt` — requested authority evidence.
- `C:/Temp/av-kit/review-r4-static-state.txt`, `review-r4-task-contract.txt`, `review-r4-scope-registry.txt`, and `review-r4-pre-edit-guard.txt` — unstarted state, task contract, registered deferrals, and canonical write-target proof.

### Open Questions / Assumptions

- No product decision is needed to resolve R4-1; it is the still-open executable predicate defect against E2's existing per-element contract.
- Runtime Electron behavior and display availability remain execution-phase risks; no runtime result is claimed here.

### Follow-Up Action

Route R4-1 through `/plan-corrections`, preserving the MEU-20 scope lock and the already-correct POST/GET `E2E_SEAM` envelopes. Do not begin implementation while this High finding remains open.

### Verdict

`changes_required` — one High-confidence, High-severity finding remains. The plan's E2E gate can still pass while the required control locator is not the target of the accepted assertion/action, so the plan is not executable to the stated MEU-20 objective as written.

### Residual Risk

This was a static plan recheck. No project tests or plan assertion scripts were run. The route-specific fixture envelopes are now correct; runtime Electron/display behavior remains unverified and belongs to execution.

## Corrections Applied (2026-08-20) — after Round 4 (human cap exception)

**Workflow**: `/plan-corrections` inside `/create-plan` §5b. USER_EXPLICIT 2026-08-20: “continue review until approved” — authorizes continuing past the plan-review cap of 3.
**Agent**: coordinator (implementer) — `corrections_applied`, never `approved`.
**Write scope**: plan/task + `assert-e2e-control-census.ps1` only.

| # | Sev | Status | Fix |
|---|-----|--------|-----|
| R4-1 | High | fixed | `Test-HasBound` now requires the allowed method to be chained on the same `getByTestId('id')` expression (`expect(...getByTestId('id')).toBeVisible()` or `getByTestId('id').click()`). The R4-1 unrelated-receiver snippet is an embedded fail-closed oracle. |

### Declared variants swept

Old: `before the next getByTestId`, `{0,120}` proximity, leftover `one matcher per block`.
New / semantic: `same-expression`, `unrelated receiver`, `Test-HasBound`.

Manifest: `C:/Temp/av-kit/census-p6-dl-r4-manifest.txt`. Runner: `C:/Temp/av-kit/census-p6-dl-r4-run.txt`.
Receiver oracle: `C:/Temp/av-kit/e2e-per-control-r4-oracle.txt` (`PASS: E2E_RECEIVER_ORACLE`).

Blast-radius census: 3 old + 3 new = 6 sweeps. Zero-hit stale: 3. Nonzero raw hits: 15. Each dispositioned below. No truncation.

### Zero-hit old receipts

| Receipt | Hits | Disposition |
|---------|------|-------------|
| `C:/Temp/av-kit/census-p6-dl-r4-before-next-old.txt` | 0 | proximity-before-next language removed |
| `C:/Temp/av-kit/census-p6-dl-r4-proximity-120-old.txt` | 0 | `{0,120}` regex removed |
| `C:/Temp/av-kit/census-p6-dl-r4-one-matcher-keep.txt` | 0 | prior prohibition phrase no longer live |

### Per-hit disposition — `same-expression` (5)

Receipt: `C:/Temp/av-kit/census-p6-dl-r4-same-expression-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `assert-e2e-control-census.ps1:31` | updated — Assert-HasBound error |
| 2 | `assert-e2e-control-census.ps1:43` | updated — expect oracle |
| 3 | `assert-e2e-control-census.ps1:47` | updated — click oracle |
| 4 | `implementation-plan.md:127` | updated — `E2E_CONTROL_CENSUS` |
| 5 | `task.md:46` | updated — row 3 |

### Per-hit disposition — `unrelated receiver` (3)

Receipt: `C:/Temp/av-kit/census-p6-dl-r4-unrelated-receiver-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `task.md:46` | updated — row 3 |
| 2 | `assert-e2e-control-census.ps1:39` | updated — R4-1 oracle |
| 3 | `implementation-plan.md:123` | updated — `E2E_PER_CONTROL` |

### Per-hit disposition — `Test-HasBound` (7)

Receipt: `C:/Temp/av-kit/census-p6-dl-r4-test-has-bound-new.txt`

| # | file:line | Disposition |
|---|-----------|-------------|
| 1 | `implementation-plan.md:123` | updated — named-set owner |
| 2 | `assert-e2e-control-census.ps1:6` | updated — header |
| 3 | `assert-e2e-control-census.ps1:23` | updated — function |
| 4 | `assert-e2e-control-census.ps1:30` | updated — Assert wrapper |
| 5 | `assert-e2e-control-census.ps1:38` | updated — false-pass oracle |
| 6 | `assert-e2e-control-census.ps1:42` | updated — expect oracle |
| 7 | `assert-e2e-control-census.ps1:46` | updated — click oracle |

---

## Recheck (2026-08-20) — Round 5 (Human Cap Exception)

**Workflow**: `/plan-critical-review` recheck after the Round-4 `/plan-corrections` pass  
**Agent**: `gpt-5.6-sol`  
**Review Mode**: `plan`  
**Verdict**: `approved`  
**Cap authority**: `USER_EXPLICIT` 2026-08-20 — “continue review until approved.”

### Scope

**Targets reviewed (read-only)**:

- `docs/execution/plans/2026-08-20-p6-gui-downloader/implementation-plan.md`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/task.md`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-e2e-control-census.ps1`
- `docs/execution/plans/2026-08-20-p6-gui-downloader/assert-handoff-markers.ps1`

**Checklist Applied**: IR; DR-1–DR-8; PR-1–PR-9; round-5 PR-6 pre-verdict gate; R4-1 only; G11/G30–G36/E2; MEU-20 scope lock.  
**Scope Lock**: MEU-20 only. MEU-21–25 were not required, no MEU ID was invented, and no r1/r2 finding was reopened.

### PR-6 Pre-Verdict Gate

`PASS`. The after-Round-4 correction appendix names `C:/Temp/av-kit/census-p6-dl-r4-manifest.txt`. The manifest and all six named child receipts were read directly. Excluding `[rtk]` banners and blank lines, the declared/actual hit counts are exactly `0, 0, 0, 5, 3, 7`, totaling 15 live raw `file:line` hits with `PR6_COUNT_MISMATCHES=0`. All 15 hits have an `updated` disposition in the matching `same-expression`, `unrelated receiver`, or `Test-HasBound` correction table (`DISPOSITION_CHECKS=15`, `DISPOSITION_MISSING=0`). No receipt contains a truncation marker.

### Intent Anchor

Executing this plan is supposed to replace the Session 7 shell at `/` with the complete MEU-20 Downloader page, prove its queue, SABR, cookie, palette, polling, and Electron behavior against the approved MEU-15/19 surfaces, and stop before MEU-21–25. The corrected receiver-bound E2E census now rejects the concrete R4-1 false pass and accepts the required same-expression assertion/action forms, so the plan is executable as written for that objective.

### Findings

No Critical, High, Medium, or Low findings.

### Round-4 Finding Adjudication

| Round-4 Item | Prior Status | Recheck Result | Evidence |
|--------------|--------------|----------------|----------|
| R4-1 — `Test-HasBound` accepted an unrelated receiver | open High | ✅ Fixed | `Test-HasBound` now builds the matcher from the literal `getByTestId('<id>')` expression followed only by an optional `expect(...)` closing parenthesis and the allowed chained method (`assert-e2e-control-census.ps1:23-27`). The embedded unrelated-receiver oracle fails closed, while the same-expression `expect(...).toBeVisible()` and direct `.click()` oracles pass (`assert-e2e-control-census.ps1:36-49`). Independent static proof: `FALSE_PASS_ACCEPTED=False`, `EXPECT_ACCEPTED=True`, `CLICK_ACCEPTED=True`, `PASS: R4-1_STATIC_REGEX_ORACLE`. |

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| All AC have source labels | pass | AC-20.1–20.22 remain source-labeled; the R4 correction changes no AC source basis. |
| Validation cells are exact commands | pass | Task row 3 names the plan-owned census script, receipt, build, and targeted Playwright files; its helper now enforces the receiver-bound predicate. |
| BUILD_PLAN audit row present | pass | Task row 5 remains the MEU-20 hub/SSOT audit and preserves the prior phase-6 plan slash. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/closeout rows remain present and ordered after implementation. |

#### Documentation Review (DR-1–DR-8)

| Check | Result | Evidence |
|-------|--------|----------|
| DR-1 Claim-to-state match | pass | The Round-4 correction claim matches the current helper and the independent three-case static oracle. |
| DR-2 Residual old terms | pass | The three stale proximity/block-level census receipts have zero non-banner hits. |
| DR-3 Downstream references updated | pass | `E2E_PER_CONTROL`, `E2E_CONTROL_CENSUS`, and task row 3 consistently state same-expression receiver binding. |
| DR-4 Verification robustness | pass | The exact R4-1 unrelated-receiver sequence returns false; both required same-expression forms return true. |
| DR-5 Evidence auditability | pass | Manifest, six child receipts, 15 per-hit dispositions, preserved correction appendix, optional oracle, and independent static oracle are reproducible. |
| DR-6 Cross-reference integrity | pass | The helper, plan named sets, task validation, E2 per-control rule, and GUI shipping gate are consistent. |
| DR-7 Evidence freshness | pass | Round-4 manifest/children were re-read in this pass and their declared counts were independently reproduced. |
| DR-8 Completion vs residual risk | pass | All 18 actionable task rows remain unchecked; the Downloader page, Wave 1 test, MEU-20 handoff, and implementation-review file are absent. |

#### Plan Review (PR-1–PR-9)

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | WP-20a–e and task rows 1–5 remain aligned; both carry the corrected E2E receiver-bound gate. |
| PR-2 Not-started confirmation | pass | Eighteen actionable rows remain `[ ]`; the named implementation/E2E/handoff/review artifacts do not exist. |
| PR-3 Task contract completeness | pass | All 18 actionable rows retain owner, deliverable, validation, dependency/context/durable-output, and status fields. |
| PR-4 Validation realism | pass | The material R4-1 false pass is rejected, and the two required legitimate forms are accepted. |
| PR-5 Source-backed planning | pass | The corrected predicate implements E2's per-element assertion requirement and the build-plan GUI shipping gate without adding product behavior. |
| PR-6 Handoff/corrections readiness | pass | Six receipt files are present and untruncated; counts match; all 15 live hits are dispositioned. |
| PR-7 Scope discipline (C2) | pass | MEU-21–25 remain evidence-backed deferrals; this pass requires no later-MEU work and invents no IDs. |
| PR-8 Control reachability/totality | pass | `Test-HasBound` now binds each accepted visual/enabled/action method to the required locator expression and fails closed on the concrete unrelated receiver. |
| PR-9 Single-statement discipline | pass | `E2E_PER_CONTROL` owns the rule and `Test-HasBound` owns its executable predicate; plan/task references are consistent. |

### Commands Executed

- Static redirected reads only (`Get-Content`, `rg`, `Test-Path`, and PowerShell receipt/count/regex inspection); no project tests, pytest, Vitest, Playwright, or plan assertion scripts were run.
- `C:/Temp/av-kit/r5-pr6-manifest-read.txt`, `r5-pr6-child-receipts.txt`, `r5-pr6-count-audit.txt`, and `r5-pr6-disposition-audit.txt` — PR-6 manifest, all six children, exact non-banner counts, and all 15 dispositions.
- `C:/Temp/av-kit/r5-plan-lines.txt`, `r5-task-lines.txt`, and `r5-plan-scripts.txt` — line-numbered/read-only review targets.
- `C:/Temp/av-kit/r5-gui-authority-lines.txt`, `r5-rest-authority-lines.txt`, `r5-emerging-lines.txt`, and `r5-download-service-lines.txt` — requested source authorities.
- `C:/Temp/av-kit/r5-r4-oracle-read.txt` and `r5-r4-static-regex-oracle.txt` — preserved and independently reproduced receiver-binding evidence.
- `C:/Temp/av-kit/r5-unstarted-state.txt` and `r5-pre-edit-guard.txt` — not-started state and canonical write-target proof.
- A scoped `git status` probe returned exit 128 because `P:/av-kit` has no `.git` directory; no verdict claim depends on Git evidence.

### Open Questions / Assumptions

None. R4-1 is deterministic from the current helper and E2 contract; no product decision or scope expansion is required.

### Follow-Up Action

No `/plan-corrections` action remains. This review workflow stops at the approved plan; implementation is outside this review pass.

### Verdict

`approved` — PR-6 passes, R4-1 is fixed, and there are zero High/Critical findings. The plan is executable as written for MEU-20.

### Residual Risk

This was a static plan recheck. No project test or Electron runtime result is claimed. Execution must still produce the plan's Red/Green, Playwright, quality-gate, handoff, and independent implementation-review evidence; a genuine no-display environment may block only the E2E run under the plan's evidence-gated `[B]` rule.
