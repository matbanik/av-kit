---
date: 2026-09-26
review_mode: plan
target_plan: docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md
verdict: approved
round: 2
findings_count: 0
template_version: "2.1"
requested_verbosity: standard
agent: "GPT-6 Astra independent reviewer"
reasoning_effort: high
summary: "Round 2 approved; all seven Round 1 findings resolved at plan level. Nonblocking notes: make harness output paths absolute and align completion predicates with task status formatting and valid blocked rows."
---

# P11 Layout Canon and Shared Primitives — Plan Critical Review, Round 1

## Intent Anchor

Session 23 is supposed to turn all 37 mockup §06 questions into one source-backed Phase 11 layout canon, then build five tested but unwired shared GUI primitives without changing page composition, APIs, persisted mutations, enablement rules, or existing test-ID strings. Executing the current draft would not yet deliver that objective with auditable evidence: the E2E contract is unresolved, the Transcript decision would leave live downstream sources contradictory, and several task gates can pass without proving their claimed state.

## Findings

| ID | Severity | Rubric | Finding | Evidence | Required correction |
|---|---|---|---|---|---|
| F1 | High | PR-4, PR-5, PR-7 | The plan expressly defers every new primitive E2E assertion to MEU-52–58 and makes a new Session 23 E2E wave out of scope, but the governing GUI plan gate and E2 require every newly created interactive element to have an E2E assertion **written and wired in this plan**. Keeping only the pre-existing Electron waves green cannot exercise `Disclosure`, `SegmentedControl`, or `PathRow` because the plan also forbids mounting them. This is a direct P1 quality-rule versus Session 23 grouping conflict, not a deferrable implementation detail. | `implementation-plan.md:178-184`, `implementation-plan.md:190-193`, `implementation-plan.md:217`, `implementation-plan.md:244-246`, `implementation-plan.md:260-263`; `task.md:46`; `.agent/workflows/create-plan.md:245-264`; `.agent/docs/emerging-standards.md:1167-1185`; `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md:68`, `:144-162` | Obtain the outstanding human decision and encode it consistently. Concrete question: **Should Session 23 add a reachable Electron-only primitive harness plus written/wired behavior assertions now, revising “zero new E2E waves,” or does the user explicitly approve a bounded exception to §4A/E2 for these unwired primitives?** Reviewer approval alone cannot waive this P1 rule. |
| F2 | High | PR-1, PR-5, DR-3, DR-6 | The three-action Transcript choice is source-resolvable, but the plan does not reconcile the two live downstream descriptions that still require a four-slot toolbar. The Phase 11 mutation lock forbids the new Clear-finished mutation, and the mockup explicitly says to ship three slots when that action is out of scope; therefore the unanswered toolbar prompt is **not essential** unless the user wants to widen behavior. However, executing the listed files/tasks leaves the grouping and generated registry/SSOT description saying four slots, defeating MEU-50’s “resolve once, in one place” objective and giving MEU-55 contradictory inputs. | `implementation-plan.md:67`, `implementation-plan.md:95`, `implementation-plan.md:122`, `implementation-plan.md:254-259`; `task.md:47`; `docs/BUILD_PLAN.md:98`; `docs/proposals/2026-09-03-transcript-page-layout-mockup.html:391`, `:401-408`; `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md:84`, `:187-190`; `.agent/context/meu-registry.md:152`; `.agent/context/meu-status.yaml:1547-1557` | Keep the source-backed three-action decision unless the user explicitly chooses a scope change, and add exact plan/task work plus validation to reconcile or formally supersede the grouping and MEU-55 registry/SSOT descriptions. If four slots are desired, obtain a Human-approved nonmutating fourth action or explicit mutation-lock change first. |
| F3 | High | PR-4, PR-8 | Both Red-phase commands convert **every** nonzero Vitest exit into success. A missing dependency, syntax/configuration error, zero-test collection, or unrelated failing test therefore satisfies the task even though the surrounding prose says only named AC failures count. This is a demonstrated false-pass of the mandatory FAIL_TO_PASS evidence gate. | `task.md:30`, `task.md:35`, `task.md:40`; `implementation-plan.md:229`, `implementation-plan.md:233-234`; `AGENTS.md` §FIC-Based TDD Workflow | Make each Red gate fail closed: require a nonzero test exit **and** prove the intended AC-specific failures/test collection from a machine-readable or exact receipt; reject infrastructure/configuration/no-test failures. Preserve the verified Red receipt for each MEU. |
| F4 | High | PR-3, PR-4, PR-8 | H1-3 claims it updates MEU-50/51 to `ready_for_review` and binds this plan, but supplies no exact update commands and validates only `render --check`. That command checks generated-view drift, not the two required state transitions. The current source has both MEUs `pending` with `execution_plan: null`, so a consistent but unchanged SSOT can satisfy the listed validation while the deliverable is materially absent. | `task.md:47`; `.agent/context/meu-status.yaml:1422-1446`, `:1447-1470`; `tools/meu_status.py:6-12`, `:225-240` | Add exact `meu_status.py update` commands for both MEUs with the plan binding, then a postcondition query that fails unless both exact blocks contain `status: ready_for_review` and the expected execution-plan path before render/check is accepted. |
| F5 | High | PR-4, PR-8 | H2-4 says it runs completion-preflight structural checks, but its command only tests whether four receipt files exist. Redirection creates a receipt even when the producing command fails, so failed handoff, review, reflection, or metrics checks still make H2-4 print `PASS closeout receipts`. The promised final no-unchecked check after H2-5 is also absent. This can false-pass the repository’s DONE gate. | `task.md:57-58`; `AGENTS.md` §Persistence & Definition of Done; `.agent/skills/completion-preflight/SKILL.md` (required by `AGENTS.md`) | Replace receipt-existence checks with the actual completion-preflight structural/postcondition checks, validate each receipt’s success evidence rather than mere presence, and add the stated final all-rows/no-unchecked gate after H2-5. |
| F6 | Medium | PR-3, PR-4 | H2-3 declares a session digest deliverable at a literal `{session-id}` path, but the only validation checks the metrics row. The row can be marked complete with no digest and no resolved session path. | `task.md:56` | Resolve the concrete session digest path and add a non-vacuous existence/content check for it, or remove the digest from this row if it is not a required deliverable. |
| F7 | Low | DR-1, DR-7 | The BUILD_PLAN audit starts from stale prose: the hub already contains Phase 11 links at lines 34 and 119, while the plan says the Phase Specs table lacks a live link. The proposed OR-based `rg` audit already succeeds against the current file and does not require the stale “registered, not yet specced” text to change. This is clerical because AC-50.6 can carry the substantive postcondition once its test is written. | `implementation-plan.md:157`, `implementation-plan.md:221-224`; `task.md:38`; `docs/BUILD_PLAN.md:34-36`, `:55`, `:119` | Correct the current-state description and make the audit assert the post-execution status/link text, not the mere presence of any one already-existing token. |

No Critical findings were identified.

## Scope Reviewed

Primary targets:

- `docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md`
- `docs/execution/plans/2026-09-26-p11-layout-canon/task.md`

Authorities and current state checked:

- `AGENTS.md`, `GUARDRAILS.md`, `PROJECT-PROFILE.md`, harness/session context, the plan-review workflow, reviewer role, and review template
- `docs/BUILD_PLAN.md`, Phase 11 grouping, MEU registry/status, and the approved MEU-49 prerequisite state
- All six `2026-09-03-*-page-layout-mockup.html` §04–§06 surfaces
- `create-plan.md` §4A, emerging standard E2, testing strategy, GUI/build-plan authorities cited by the plan, and the MEU-49 reflection carry-forward
- Current UI scripts, test-ID registry, relevant component/page state, referenced executable paths, and repository worktree state

The plan is genuinely unstarted: the two proposed unit tests, five primitive components, Phase 11 canon, MEU-50/51 handoffs, and implementation review do not exist. No project tests, CI gates, generators, migrations, network/data probes, or `tools/` scripts were run.

## Verification Performed

| Check | Result |
|---|---|
| §06 decision census | Pass: 4 Downloader + 7 Convert + 6 Transcript + 7 TTS + 6 Capture + 7 Settings = exactly 37; plan IDs map one-for-one and preserve the mockup order. |
| Decision-source trace | Pass with F2 correction: the 37 choices are supportable through the mockup proposal/current-behavior alternatives plus `COMPOSITION_LOCK`; the three-action Transcript choice follows the mockup’s explicit conditional. Live four-slot descriptions remain unreconciled. |
| MEU-50/51 scope | Pass: registry, status, grouping, and task order consistently assign canon/tokens first and five unwired primitives second; downstream page composition is scheduled to MEU-52–58. |
| Out-of-scope MEU references | Pass: MEU-52–58 exist in registry/status and match the named deferred page surfaces. The E2E row itself fails the higher-priority GUI gate per F1. |
| Referenced executable/artifact existence | Pass for current executables: `ui/package.json`, `tools/meu_status.py`, `tools/check_exec_review.py`, handoff/reflection templates, schema, metrics file, styles, and test-ID registry exist. Missing canon/tests/components/handoffs are explicitly scheduled outputs. The three GUI reference/index authorities cited by §4A are absent and the plan accurately says so. |
| Command/package mapping | Pass for command names: UI scripts expose `test`, `typecheck`, `lint`, `build`, and `test:e2e`; the review checker accepts the listed flags. Semantic false-passes remain in F3–F5. |
| Not-started state | Pass: all implementation rows are unchecked and no correlated implementation handoff or planned implementation file exists. |
| Review-file mode | Pass: canonical Round 1 path did not pre-exist; this file is the sole permitted write. |

Static evidence receipts include `C:/Temp/av-kit/session23-mockup-06.txt`, `session23-authority-hits.txt`, `session23-gui-policy-hits.txt`, `session23-unstarted-state.txt`, `session23-command-paths.txt`, `session23-meu-state.txt`, `session23-path-census.txt`, `session23-literal-conflicts.txt`, and `session23-task-numbered.txt`.

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Notes |
|---|---|---|
| All AC have source labels | Pass with correction | AC labels use allowed source classes; F1 is an unresolved conflict between two cited authorities, and F2 requires downstream source reconciliation. |
| Validation cells are exact commands | Fail | F3–F5 demonstrate commands that can pass without the claimed prerequisite, Red evidence, SSOT state, or closeout state. |
| BUILD_PLAN audit row present | Pass with Low correction | Present, but its baseline claim and grep postcondition are stale/vacuous (F7). |
| Post-MEU rows present | Pass with correction | H1/H2 ordering is complete, but H2-3/H2-4 evidence is incomplete (F5–F6). |

### Documentation Review (DR-1 through DR-8)

| Rule | Result | Notes |
|---|---|---|
| DR-1 Claim-to-state match | Partial | Unstarted claims and MEU state match; BUILD_PLAN “missing link” prose does not. |
| DR-2 Residual old terms | Fail | Four-slot Transcript descriptions remain live beside the planned three-slot canon. |
| DR-3 Downstream references | Fail | Grouping and MEU registry/status descriptions are not scheduled for substantive reconciliation. |
| DR-4 Verification robustness | Fail | Red, SSOT, and closeout commands admit concrete false-passes. |
| DR-5 Evidence auditability | Partial | Receipt routing and executable paths are sound; several receipts do not prove their named postconditions. |
| DR-6 Cross-reference integrity | Fail | F1 and F2 leave explicit authority conflicts unresolved. |
| DR-7 Evidence freshness | Partial | Current MEU state and file existence were checked; the BUILD_PLAN baseline statement is stale. |
| DR-8 Completion vs residual risk | Pass | The draft does not claim implementation completion. |

### Plan Review (PR-1 through PR-9)

| Rule | Result | Notes |
|---|---|---|
| PR-1 Plan/task alignment | Partial | MEU order and outputs align; the task does not carry the registry/grouping reconciliation needed by TR1. |
| PR-2 Not-started confirmation | Pass | Proposed implementation artifacts and handoffs are absent; task rows are unchecked. |
| PR-3 Task contract completeness | Fail | H1-3 lacks exact state-update commands; H2-3 leaves the digest path/validation unresolved. |
| PR-4 Validation realism | Fail | F3–F5 are substantive false-passing gates. |
| PR-5 Source-backed planning | Fail | The 37-choice census is sound, but the E2 conflict requires a human resolution and TR1’s downstream sources remain contradictory. |
| PR-6 Handoff/corrections readiness | Pass | Separate MEU handoffs and rolling plan/implementation review paths are explicit. |
| PR-7 Scope discipline | Fail | Deferred page work maps to real MEUs, but written/wired E2E is incorrectly classified out of scope against a mandatory rule. |
| PR-8 Control reachability and totality | Fail | Red, SSOT, and completion observables are not bound to fail-closed postconditions. |
| PR-9 Single-statement discipline | Pass with correction | Named sets are defined once and referenced by name; the unresolved four-slot/three-slot source conflict must be removed per F2. |

## Open Questions and Assumptions

- **Essential human decision — E2E timing:** choose between adding a reachable primitive E2E harness/assertions in Session 23 or explicitly approving a bounded §4A/E2 exception. Until answered, the plan cannot be approved.
- **Transcript toolbar:** no human answer is essential to preserve three actions. `docs/BUILD_PLAN.md:98` plus mockup §06’s “if that action is out of scope, ship three” clause resolve the product behavior. A human answer becomes essential only if four slots/new Clear-finished behavior is desired.
- Static command review only was performed, as required. Executability conclusions are based on package scripts, CLI source, path existence, and predicate logic rather than running project commands.

## Verdict

**changes_required**

The one-to-one 37-decision census and the MEU-50 → MEU-51 scope are substantially sound. Approval is blocked because the mandatory GUI E2E timing conflict still needs the user’s explicit resolution, the three-action Transcript choice would leave live four-slot authorities contradictory, and the Red/SSOT/closeout gates can materially false-pass. Apply corrections through `/plan-corrections`, then return the plan and task together for Round 2 with the required untruncated blast-radius census and per-hit dispositions.

## Follow-up Actions

1. Resolve F1 through the outstanding human E2E decision and encode the chosen scope in both plan and task.
2. Preserve the three-action Transcript recommendation unless the user widens behavior, and reconcile every four-slot grouping/registry/status hit (F2).
3. Replace the Red commands with AC-specific fail-closed oracles (F3).
4. Add exact MEU update commands and exact postconditions for H1-3 (F4).
5. Replace H2-4’s receipt-existence check with actual completion-preflight validation and add the final no-unchecked gate (F5).
6. Resolve the session digest path/validation and refresh the BUILD_PLAN audit baseline (F6–F7).

## Recheck

Not applicable in Round 1. No plan, task, product code, test, or source document was modified by this review.

## 2026-09-26 Orchestrator Correction Checkpoint — Human Decision Pending

This section records **planner corrections**, not an independent review verdict. Frontmatter remains `changes_required`; no Round 2 dispatch or self-approval has occurred. F1 remains open pending the user's explicit §4A/E2 choice.

| Finding | Correction now in the plan/task | Verification/disposition |
|---|---|---|
| F2 | AC-50.4 and task row 3 require the grouping and MEU-55 SSOT description to use TR1's three-action toolbar; H1-3 renders and asserts the generated registry description. | The historical Transcript mockup remains a source input. Downloader/Convert four-slot wording is unrelated. The two grouping hits, MEU-55 YAML hit, and generated registry hit are scheduled for execution reconciliation. |
| F3 | Task rows 2 and 7 use Vitest JSON reporter receipts and `RED_ORACLE`: exact test file, all AC titles collected, a failed AC `AssertionError`, no file-level collection error or pending/todo tests, and nonzero Vitest exit. | JSON field names were read from the installed Vitest 3 reporter. The old unconditional nonzero-as-pass predicate has zero remaining plan/task hits. |
| F4 | H1-3 names both `meu_status.py update` invocations with `--plan`, render/check, and exact YAML state/plan plus generated MEU-55 postconditions. | `render --check` remains only inside the full transition chain. |
| F5 | H2-4 checks handoff size/markers/AC coverage, reruns the independent review-state checker, validates reflection/metrics/digest, and requires the 20 prior rows complete. A separate final gate after H2-5 checks all 22 task rows. | The prior receipt-existence-only PASS predicate has zero remaining plan/task hits. |
| F6 | `SESSION_DIGEST` names the current Codex conversation directory and H2-3 checks its size/target plus the populated metrics row. | If execution resumes in a different conversation, the path must be updated before H2-3. |
| F7 | The plan now states that Phase 11 hub links already exist; task row 5 requires their target, rejects stale prose, and asserts the exact replacement sentence. | Old prose appears only as the baseline or a negative oracle in the plan/task. |
| Additional | Task row 1 now checks the exact MEU-49 block; H1-4 fails if the API status contains a real changed path. | Static PowerShell parse checked all 22 task-row commands: 0 syntax errors (`C:/Temp/av-kit/p11-task-pwsh-parse.txt`). |

### Correction blast-radius census, provisional

All listed `rg -F -n` receipts are untruncated and cover **both** `implementation-plan.md` and `task.md`. Semantic variants were also swept across `.agent/` and `docs/` in `C:/Temp/av-kit/p11-crossdoc-toolbar.txt` and `C:/Temp/av-kit/p11-crossdoc-hub.txt`.

| Changed value | Old/new receipts | Per-hit disposition |
|---|---|---|
| Transcript `4-slot header toolbar` → `three-action header toolbar` | `p11-census-toolbar-old.txt`; `p11-census-toolbar-new.txt` | Old hit in task H1-3 is an intentional negative postcondition; new hits in task row 3 and H1-3 are updated. Cross-doc source hits: grouping:84,188 and MEU-55 SSOT:1556 are scheduled edits; generated registry:152 is scheduled render. Transcript mockup:187 remains historical input; Convert mockup:456 is a different page. |
| Hub “registered, not yet specced” → exact specced sentence | `p11-census-hub-old.txt`; `p11-census-hub-new.txt` | Old hits in task row 5 and plan AC-50.6/audit are explicit baseline or rejection checks; new hits in task row 5 and plan audit prose/command are updated. Live BUILD_PLAN:36 remains the execution target. |
| Nonzero test exit → `RED_ORACLE` | `p11-census-red-old.txt`; `p11-census-red-new.txt` | Old unconditional predicate has zero hits. New hits are the named definition, two task Red commands, and two verification references. |
| Bare `render --check` → exact SSOT transition | `p11-census-status-old.txt`; `p11-census-status-new.txt` | One remaining render check is a required step inside H1-3's update/render/postcondition chain; its presence is confirmed consistent. |
| `{session-id}` → concrete `SESSION_DIGEST` | `p11-census-digest-old.txt`; `p11-census-digest-new.txt` | Placeholder has zero hits; current conversation ID appears in plan definition and task H2-3/H2-4. |
| Receipt existence PASS → structural closeout PASS | `p11-census-closeout-old.txt`; `p11-census-closeout-new.txt` | Old PASS string has zero hits; new PASS is emitted only after H2-4's substantive checks. |

The census will be rerun after F1 is resolved and before a GPT-6 Astra / high Round 2 submission, per the user's model instruction. No project tests or scripts were executed during these planning corrections.

## 2026-09-26 Corrections Applied — Round 2 Ready

This is an orchestrator correction log, **not** an independent approval. Round 1's seven findings remain the review history. The user explicitly chose Option 1 on 2026-09-26: Session 23 adds a reachable, isolated Electron primitive harness and written/wired E2E assertions. `implementation-plan.md` and `task.md` now make that `Human-approved` choice concrete as `E2E_HARNESS` and AC-51.7. No product page mount is planned; MEU-52–58 retain their page-specific E2E duties. The grouping's old Session 23 “zero new E2E waves” prose is an execution reconciliation target in task rows 3/H1-3, together with the earlier TR1 description corrections.

The separate build output `ui/out-e2e` is reachable through real Electron main and a separate BrowserWindow. `AVKIT_PRIMITIVE_HARNESS_BUILD=1` conditionally adds the renderer HTML; `AVKIT_E2E_OUT_DIR` selects only `out` or `out-e2e`. The task requires a real Playwright behavior wave, selected-build freshness, an ordinary product build with no harness HTML, and confirmation that `electron-builder.yml` packages only `out/**/*`. A new implementation row makes 11 implementation rows, 21 pre-closeout rows, and 23 total rows. F2–F7 corrections in the prior checkpoint remain in force.

### Final correction blast-radius census

Every old/new literal was swept with unfiltered `rtk proxy rg -F -n` over **both** plan files. The nine pairs, 18 complete receipts, and hit counts are in `C:/Temp/av-kit/p11-census-summary.txt` and `C:/Temp/av-kit/p11-census-f*-old.txt` / `-new.txt`. The static task audit receipt is `C:/Temp/av-kit/p11-static-audit.txt`: 23 rows, 23 PowerShell validation commands parsed, 10 unescaped table delimiters per row, and no listed stale plan phrase. These are static checks; no project test/build/script ran during correction.

| Changed value and variants | Old/new hits | Per-hit disposition |
|---|---:|---|
| F1 “zero new E2E waves” → `E2E_HARNESS` | 0 / 6 | New: plan:75 defines it, :170 limits mount, :192 binds AC-51.7, :233 keeps consumer page assertions scheduled, :267 binds GUI gate; task:43 implements it. All six are updated and consistent. |
| F1 “no new user-visible control is mounted” → test-only wave | 0 / 10 | New: plan:18/59 establish scope and user decision, :179 validates build input, :203 classifies decision, :222 schedules grouping edit, :267/283 cover GUI gate and resolved decision; task:36/43/48 schedule grouping, harness, and closeout reconciliation. All ten are updated and consistent. |
| F2 “4-slot header toolbar” → “three-action header toolbar” | 1 / 2 | Old task:48 is the intentional fail-closed generated-registry rejection. New task:36/48 schedule the source edit and assert the generated postcondition. Grouping:84/188, MEU-55 YAML:1556, and generated registry:152 remain explicit execution targets; the historical mockup and other pages are not rewritten in planning. |
| F3 unconditional nonzero Red → `RED_ORACLE` | 0 / 5 | New definition and AC-50/51 Red references are consistent. Task:35/40 validate exact JSON collection, every AC title, a failed assertion, and no collection/pending/todo false pass. AC-51.7's static unit assertion fails in Red on missing harness/E2E wiring; its real Electron assertion runs after build. |
| F4 bare `render --check` → exact state transition | 1 / 2 | Old task:48 is retained only as a step inside the update → render → check → YAML/registry postcondition chain; new task:48 and plan:260 bind `ready_for_review` and the plan path. |
| F5 “20 prior rows” → “21 prior rows”; “22 task rows” → “23 task rows” | 0/1 and 0/1 | New task H2-4:58 checks 21 previous rows; final gate:74 checks all 23. H1-1:46 checks 11 implementation rows. Plan:262 states the same 23-row total. All counts match the 11+7+5 task rows. |
| F6 `{session-id}` → `SESSION_DIGEST` | 0 / 2 | New plan:77 defines the concrete conversation path and migration rule; task H2-3:57 checks that path's content and size. H2-4:58 independently checks its existence/size. |
| F7 stale hub baseline → exact replacement sentence | 4 / 3 | Old task:38, plan:140/237/240 are intentional baseline or negative-oracle hits. New task:38 and plan:237/240 require the same exact replacement and link target. |

Semantic variants swept in `C:/Temp/av-kit/p11-stale-scope.txt`, `p11-e2e-crossdoc.txt`, `p11-crossdoc-toolbar.txt`, and `p11-crossdoc-hub.txt`: the old grouping:68 and :144–148 statements are deliberately scheduled for execution rewrite, not treated as already fixed. Cross-doc sweep checked the grouping, MEU SSOT and generated registry, BUILD_PLAN, build-priority matrix, GUI policy, and create-plan gate; the correction edits only the two plan files and this rolling review file. Round 2 must independently judge the plan; this correction log is not a reviewer verdict.

---

## Independent Round 2 Review — 2026-09-26

**Workflow:** `/plan-critical-review` · **Mode:** `plan` · **Reviewer:** GPT-6 Astra, high reasoning effort (user-directed).

### Intent Anchor

Session 23 must establish the 37-decision Phase 11 canon and five shared primitives, with a reachable Electron-only harness and written/wired interaction assertions, while leaving product pages and backend behavior unchanged. The corrected design can deliver that objective: the human-approved harness resolves the previous E2E scope conflict, and the plan now schedules the source reconciliation and substantive evidence gates that Round 1 found missing.

### Findings

**No remaining High/Critical findings. Verdict: `approved`; `findings_count: 0`.** The two nonblocking correction notes below are intentionally outside the structured findings count, as required by the workflow's Verdict Rule. This approves a plan, not implementation evidence.

### Prior Pass Summary and Confirmed Fixes

References to `implementation-plan.md` and `task.md` below are relative to `docs/execution/plans/2026-09-26-p11-layout-canon/`.

| Finding | Round 2 result | Independently checked evidence |
|---|---|---|
| F1 — E2E timing/reachability | Resolved at plan level | The explicit Option 1 decision is `Human-approved` at plan:59,75,203. AC-51.7 and plan:194 require the real components, a separate Electron BrowserWindow, behavior/visual assertions, pre-implementation unit/E2E test authoring, and fresh isolated output. Task:40,43 wires and runs the new wave; plan:222 and task:36,48 reconcile grouping prose. This meets `create-plan.md:258` and emerging standard E2:1167–1185 without mounting a product page. See the build-path correction note below. |
| F2 — Transcript downstream contradiction | Resolved at plan level | TR1 remains three existing actions (plan:98), supported by `docs/BUILD_PLAN.md:98` and the Transcript mockup:403. AC-50.4, plan:162–163 and task:36 explicitly edit grouping/MEU-55 SSOT; task:48 renders and rejects the old registry description. Independent semantic search found grouping:84,188, SSOT:1556 and registry:152, all scheduled targets. Their current old wording is expected before execution, not a claim that corrections already shipped. |
| F3 — nonzero exit accepted as Red | Resolved | Plan:76 and task:35,40 require a fresh JSON receipt, the named collected file, every AC title, at least one failed AC assertion containing `AssertionError`, no file collection message, and zero pending/todo tests. Installed Vitest reporter `ui/node_modules/vitest/dist/chunks/index.VByaPkjc.js:1698–1760` emits those fields, including skipped tests in `numPendingTests`. A bare dependency/configuration failure or empty collection cannot supply the required evidence. Plan:194 explicitly makes AC-51.7's unit assertion fail on absent harness wiring; real Electron assertions run after the build exists. |
| F4 — SSOT update omitted | Resolved | Task:48 now runs both exact `update MEU-N ready_for_review --plan ...` operations, checks each exit, renders/checks, then asserts both YAML blocks and the rendered TR1 description. `tools/meu_status.py:225–242` accepts these arguments. Current MEU-50/51 remain `pending` with null plans (:1434,1443,1458,1467), so unchanged SSOT cannot meet these postconditions. |
| F5 — receipt-existence closeout | Resolved; formatting note survives | Task:58 reads actual handoffs and AC coverage, checks reflection/metrics/digest, reruns the target-bound independent review validator, and checks prior task states. Task:74 adds the final 23-row gate. `tools/check_exec_review.py:101–131` rejects wrong mode/target/verdict, nonzero findings, and invalid round. Receipt existence alone no longer proves DONE. Do not reopen the fixed surface through progressively deeper predicate mutations; the remaining false-negative formatting issue is nonblocking below. |
| F6 — unresolved session digest | Resolved | Plan:77 resolves `SESSION_DIGEST` and supplies a conversation-migration rule. Task:57 requires its file, minimum content size and this project's two MEU identifiers; task:58 rechecks presence/size. The literal `{session-id}` is gone from both plan files. |
| F7 — BUILD_PLAN baseline/audit | Resolved | Plan:237 accurately distinguishes existing links from their absent target. Plan:240/task:38 require the target, exact replacement sentence, and link, and reject the old status phrase. Live hub:34,36,119 matches that stated baseline. |

### Harness, Red Evidence, and Isolation Assessment

- **Reachability:** `ui/package.json:18` runs the Playwright wrapper; `ui/scripts/playwright-with-outputfile.mjs` forwards the selected spec and exits with the child status. `ui/playwright.config.ts:12–15` discovers `layout-primitives.test.ts` and runs global setup. The planned spec launches `out-e2e/main/index.js`, creates its separate BrowserWindow and loads the conditional renderer HTML, whose TSX entry imports the five real components (plan:75,192,218–221; task:43). Existing `_electron.launch`/`AVKIT_E2E` conventions are visible at `ui/tests/e2e/download-queue.test.ts:153–161`; real main already reaches `app.whenReady()`/BrowserWindow at `ui/src/main/index.ts:454–455`. Creating the second window through Playwright's Electron main-process evaluation does not require a product router/main/preload edit. No dead-end caller is demonstrated.
- **Freshness:** current global setup only checks ordinary `out` against sources (`ui/tests/e2e/global-setup.ts:27–42`). The plan expressly schedules its replacement with allowlisted selected-output, source/config freshness and HTML-existence checks. Plan:194 separately requires the primitive spec to check its own `out-e2e` freshness during the full suite, whose global setup selects ordinary `out`. Thus a fresh product build alone cannot satisfy the stated harness contract.
- **Packaging:** the build flag conditionally adds the harness entry; ordinary build must omit it. `ui/electron-builder.yml:6–7` includes `out/**/*`, with no `out-e2e` input; its extra resources are unrelated explicit paths. Task:43 builds both forms, checks harness HTML presence/absence, and checks packaging scope. The actual archive is not built or certified by this static review; runtime execution review must verify the realized config/import graph.
- **Assertions:** AC-51.7 specifies disclosure activation/focus, radio keyboard/checked/visual state, readable chip tone/count, label/hint/error association, exact path edits and visible Browse callback evidence. These are behavior oracles, not title-only census checks. AC-51.6 registers IDs. The pre-build unit Red oracle and post-build Electron assertion serve different stages; the plan does not claim an Electron launch/configuration error is an assertion failure. The cited [Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/), [Radio Group](https://www.w3.org/WAI/ARIA/apg/patterns/radio/), and [Button](https://www.w3.org/WAI/ARIA/apg/patterns/button/) APG sources support the planned keyboard semantics.

### Nonblocking Correction Notes

1. **Low, high confidence — resolve the harness output path explicitly.** Plan:253 and task:43 pass relative `--outDir out-e2e`. Installed electron-vite applies `resetOutDir` to each target and resolves against `config.root || process.cwd()` (`ui/node_modules/electron-vite/dist/chunks/lib-q6ns0vZr.js:1589–1593,1619–1627`). The current renderer root is `ui/src/renderer` (`ui/electron.vite.config.ts:33`), so retaining it yields renderer output under `ui/src/renderer/out-e2e/renderer`, not the required `ui/out-e2e/renderer`. Pass an absolute repo-resolved `ui/out-e2e` directory in both commands, or explicitly normalize all three target outputs in the already-scheduled config edit. The intended output is unambiguous and task:43 rejects a missing intended HTML; this is a command-path correction, not a missing deliverable or false-passing gate.
2. **Low, high confidence — normalize the completion status cells once.** Task:46,58,74 predicates expect bare `[x]`/`[B]`, while the table currently wraps `[ ]` in backticks. Merely replacing its space with `x` retains backticks and fails those predicates. Also, task:58 requires `[x]` for H1-2 even though task:47/64 and plan:259 permit an evidence-backed external E2E `[B]`. Normalize the final status cell before matching and use the same evidence-backed blocked-state rule across the pre-closeout and final checks. These are false-negative predicate/formatting discrepancies, not a way to approve absent work; under Materiality Gate #1/#3 they do not reopen F5 as a blocker.

### Scope and PR-6 Census

Reviewed together: both supplied plan files, all seven Round 1 findings and both correction checkpoints, the workflow/template, AGENTS/GUARDRAILS/profile/context, §4A/E2, Phase 11 grouping/hub/matrix/MEU state, all six mockup §06 lists, the MEU-49 carry-forward, and relevant UI build/packaging/E2E/reporter and status/review-checker source. The most recent other dated plan-review exemplar was also read before writing.

**PR-6 passes.** All 18 final `p11-census-f*-old/new.txt` receipts exist and contain complete unfiltered records. Independent comparison matched all **38 hit records** to their current exact file lines; counts agree with `p11-census-summary.txt`. The final correction log:167–176 dispositions account for each record by line or uniquely identified definition/task/reference group. The six retained old-literal hit records are deliberate rejection checks/baselines (F2:1, F4:1, F7:4). No undispositioned changed-value cluster was found.

The supplemental `p11-crossdoc-toolbar.txt` and `p11-crossdoc-hub.txt` include **older intermediate plan text**, so they were not accepted as current plan evidence. Independent semantic sweeps reproduced the live source hits and checked current plan/task text instead. Historical mockup four-slot drawings and unrelated Downloader/Convert/Phase 10 actions remain source history, not live instructions to add a Transcript mutation. The six §06 lists still map to 4+7+6+7+6+7 = 37 decisions.

### Commands Executed and Evidence

All shell invocations used `rtk proxy`, all-stream receipts under `C:/Temp/av-kit/`, immediate exit-code capture and propagation. No plan validation cell was executed. No project tests, builds, CI gates, generators, migrations, data probes or `tools/` scripts ran; Python/TypeScript files were read as text. The only repository write is this rolling review.

| Static operation | Receipt / result |
|---|---|
| `rtk proxy rg -n '^'` on plan, task and rolling review | `r2-plan.txt`, `r2-task.txt`, `r2-prior-review.txt` |
| `rtk proxy git status --short` | `r2-status.txt`; unrelated existing changes were not treated as Session 23 implementation |
| Read all final census receipts, summary and supplied static audit | `r2-census-read.txt`; raw originals preserved |
| Read supplemental cross-document sweeps | `r2-crossdoc-launch.txt`, `r2-compact-census.txt` |
| Independent `rg -n -i` sweep for zero/no-new E2E, four/4-slot, three-action, Clear finished, stale hub and harness variants over plan plus live grouping/SSOT/registry/hub/matrix | `r2-semantic-sweep.txt` |
| PowerShell parser over extracted validation commands; compare each raw census record with its current source line; `Test-Path` inventory | `r2-independent-static-audit.txt`: **23 rows, 23 unchecked, 0 parse errors, 38 exact record matches** |
| Installed reporter/build implementation and repository CLI source reads | `r2-semantic-proof.txt`, `r2-installed-semantics.txt`, `r2-launch-tools-fixed.txt` |
| Six mockup §06 reads and live source pins | `r2-mockups-fixed.txt`, `r2-source-pins.txt` |
| Canonical write-path guard and plan/task SHA-256 snapshot | `r2-pre-edit.txt` |

The initial wildcard-path `rg` and an inline range-reader had read-only errors; corrected receipts are explicitly named above. An attempted read of nonexistent `smoke.test.ts` was replaced with the real `download-queue.test.ts` launch convention. None of these was represented as project validation.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | Pass with notes | Same canon, five primitives, isolated E2E, reconciliation and H1→review→H2 sequence; command notes above. |
| PR-2 Not started | Pass | 23 unchecked rows; proposed canon/components/unit/E2E/harness files and both implementation handoffs absent; MEU-50/51 pending. |
| PR-3 Task contract | Pass | All actionable rows have owner, deliverable, exact validation, dependency and status; referenced executables exist or are scheduled. |
| PR-4 Validation realism | Pass with notes | Red, SSOT and closeout substantive false-passes corrected; output/status command corrections remain nonblocking. |
| PR-5 Source-backed planning | Pass | Allowed source labels; explicit human Option 1; TR1 conditional and composition lock; APG support. |
| PR-6 Corrections readiness | Pass | 18 raw receipts, 38 current records, disposition log, explicit handoff paths. |
| PR-7 Scope discipline | Pass | Consumer work maps to existing MEU-52–58; Session 23 primitive E2E is included; backend exclusions cite the composition lock. |
| PR-8 Reachability/totality | Pass at design level | Named build→Electron→HTML→real imports→interaction chain; missing/stale/invalid-output and packaging negatives; actual runtime proof remains execution work. |
| PR-9 Single statement | Pass with clerical duplication | Named sets govern; repeated command predicates have an inferable intended value, not conflicting product behavior. |
| DR-1 / DR-7 Claim-state / freshness | Pass | Current files and final census checked directly; older supplemental receipt text explicitly identified. |
| DR-2 / DR-3 / DR-6 Terms / downstream / cross-references | Pass at plan level | Live grouping/SSOT/registry contradictions are explicitly scheduled corrections, not silently deferred. |
| DR-4 / DR-5 Robustness / auditability | Pass with notes | Substantive gate repairs verified statically against installed/current source. |
| DR-8 Completion vs risk | Pass | No implementation completion claim. |
| IR / template | Pass | Source labels, hub audit, exact commands, handoff/reflection/metrics/digest rows and v2.1 review fields present. |
| AV-1–5 | Planned, not executed | Red/Green, real assertions, no masking and no placeholders are contractual execution obligations. |
| AV-6 | Pass | Criteria traced to spec/local canon/research/human decision. |

### Verdict and Follow-up

**`approved` — Round 2, `findings_count: 0`.** No evidence-backed High/Critical delivery defect or PR-6 precondition failure remains. Apply the two command corrections without widening scope; preserve the test-first, harness isolation, source-reconciliation and independent execution-review obligations. No additional product decision is required for TR1 or the already-chosen E2E timing.

**Residual risk:** static feasibility is not a passing Electron/build/packaging receipt. Execution must demonstrate real controls, selected-build freshness, ordinary-output exclusion and unchanged existing waves. Review approval is independent of the human plan-to-execution gate; this review neither starts implementation nor grants that human approval. Per the review-only write scope, no separate reflection, focus update, plan correction or product change is made.

### Orchestrator Addendum — Reviewer-Directed Command Corrections

After receiving the independent `approved` verdict, the orchestrator applied only the two nonblocking command corrections the reviewer requested; this addendum is not a new review or verdict. Both plan:253 and task:43 now pass absolute `P:/av-kit/ui/out-e2e` to electron-vite. Task H1-1:46, H2-4:58, and final gate:74 now extract the final status cell, trim optional Markdown backticks, and accept `[x]` or a `[B]` with `follow-up:` and `receipt:` evidence. The 11/21/23 row counts and task scope are unchanged.

Static verification: `C:/Temp/av-kit/p11-static-audit-final.txt` confirms 23 task rows, 23 parseable PowerShell validation commands, and valid table delimiters; `p11-status-audit.txt` checks bare/backticked complete, blocked, and open status parsing. Unfiltered old/new sweeps are `p11-relative-out-old.txt` (0 hits), `p11-absolute-out-new.txt` (plan:253 and task:43), `p11-status-predicate-old.txt` (0 hits), and `p11-status-predicate-new.txt` (task:46,58,74). No project build or test was run at this planning gate. The Round 2 independent verdict above remains the approval record; execution still requires the driver's human plan-to-execution authorization.
