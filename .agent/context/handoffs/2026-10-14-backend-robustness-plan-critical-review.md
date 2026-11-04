---
date: "2026-10-15"
review_mode: plan
target_plan: P:/av-kit-wt/backend-robustness/docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md
verdict: approved
findings_count: 0
round: 4
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-14-backend-robustness

> **Intent anchor:** "Session 33 delivers MEU-76 (logged, CORS-safe unhandled errors and a typed extract error), MEU-78 (one live ffmpeg resolver for Convert, TTS, health and yt-dlp) and MEU-77 (TTS generate returns the job at once, synthesizes in the background and can be cancelled), with an OpenAPI diff limited to those contracts and an MCP audit in which tts.cancel passes."

**Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial.
Four High findings block approval; four findings are non-blocking. No Critical finding.
TA-1 through TA-10 are individually approved within their exact stated scope.

## Scope

Reviewed the implementation plan, task table, validate-task.ps1, exec_checks.py, plan_checks.py and baseline_carry.py ONLY in **P:/av-kit-wt/backend-robustness**, branch **claude/backend-robustness**, against the supplied residual build-plan contracts, grouping, issue SSOT, Session 30 precedent, affected production call chains and existing test expectations.

Applied the protocol's nine sweeps, PR-1–PR-9, DR-1–DR-8 and relevant reviewer adversarial checks. Author: Anthropic/Claude Code; independent reviewer: OpenAI/Codex gpt-6.1-sol. The refused first attempt was working notes only; every finding below was rechecked against the actual files. This is still Round 1, not a correction round.

Observed: HEAD **78610200ea2e7efd52318ea95c3e48b6df4993ba**, all 24 task rows unchecked, only the Session 33 plan directory untracked, tracked diff empty. The three implementation handoffs, baseline.sha and canonical plan-review file are absent. Plan mode is appropriate.

No repository file was written, and no plan/product/test file in P:/av-kit was read. Shell cwd was always the requested worktree. Writes were limited to this report and scratch receipts under C:/Temp/av-kit, plus the explicitly allowed evaluator self-test's system temporary fixtures. No product tests, builds, generators, validate-task checks or live audit were run.

The user's receipt-only write scope and final-JSON requirement supersede the workflow's canonical-write and timestamp suffix requirements. No timestamp script or extra verifier verb was executed. Completion-preflight was read and applied to review-artifact completeness; its implementation-task execution steps do not authorize implementing the unstarted plan. The dispatcher owns copying this report verbatim to the canonical review path.

## Findings

| # | Severity / Confidence | Blocking | Kind / Subject | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High / High | yes | behavior / deliverable | Cancellation is not atomic with the worker's terminal write. After the final flag check, cancel(id) can return while the row is Generating, then _finish_done commits Done and keeps the files; finally discards the flag. No shared synchronization or conditional terminal transition is specified. **Violates: AC-77** | docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md:131-134,295-296 | Specify a shared synchronization mechanism and cancellation linearization point for cancel and terminal-state selection; add a bounded barrier test cancelling between the final check and terminal commit. | open |
| F2 | High / High | yes | behavior / deliverable | SHUTDOWN_STOP ignores wait_idle(10.0) returning False. A synthesis segment or MP3 subprocess can outlast the wait, after which lifespan unloads the model and disposes the engine while the worker remains active and its row remains Generating. The planned five-second fake never exercises this branch. **Violates: AC-77** | docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md:136,144,300 | Define the timeout outcome, synchronize shutdown admission with worker registration, and prevent teardown of resources still owned by a worker. Test the timeout branch with a controlled wait result. | open |
| F3 | High / High | yes | behavior / deliverable | AUDIT_CANCEL_STEP checks Generating only when POST returns and relies on fixed long text to survive subsequent refusal probes. destructiveStep makes several awaited calls before confirmed cancellation, so the target can finish first. AC-77.13 only checks the initial response and does not prove a deterministic running-job cancellation. **Violates: AC-77** | docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md:139,304; mcp-server/scripts/audit/plan.ts:231-260 | Observe and handle loss of the running precondition through the refusal sequence, re-establish the target with bounded retries, and require an actual Cancelled terminal result. Cover completion before the confirmed call. | open |
| F4 | High / High | yes | control-defeat / committable-tooling | The audit fingerprint is first measured after the audit finishes. If a gated source changes after build/import but before fingerprinting, the audit of tree A is labelled with tree B's identity. A subsequent Windows gate on B and gate-check can agree, falsely accepting H1-2/H1-4 evidence for the reviewed tree. **mechanism: task-row-completion-predicate** **Violates: AC-77** | docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1:301-326; docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py:501-514 | Capture AUDIT_FINGERPRINT before audit preparation/build and after completion, excluding only the generated baseline as intended; require equality and compare that identity with the final gate and current reviewed tree. | open |
| F5 | Medium / High | no | behavior / committable-tooling | After the first successful audit writes tts.cancel=pass to the baseline, every later successful audit produces delta UNCHANGED. AUDIT_EXPECT still requires FIXED, so H1-8's mandatory audit rerun after a gated correction fails and rollback restores the same pass baseline. **Violates: AC-77** | docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py:360-362; docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1:300,307-322; docs/execution/plans/2026-10-14-backend-robustness/task.md:58; mcp-server/scripts/audit/classify.ts:116-126 | Keep immutable pre-session comparison evidence for all attempts, or distinguish first FIXED proof from subsequent all-pass revalidation linked to it. Preserve automatic rollback and baseline annotation restrictions. | open |
| F6 | Medium / High | no | control-defeat / committable-tooling | GATED_PATHS omits actual full-gate inputs beyond its stated SSOT exclusions: the older layout plan/grouping, audit workflow/index READMEs, commands.md and TASK-TEMPLATE.md. Those files can change after the gate without changing its fingerprint. The plan contract and baseline_carry.py are also excluded. **mechanism: task-row-completion-predicate** | docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md:146; ui/tests/unit/layout-canon.test.ts:15-19; mcp-server/tests/audit/docs.test.ts:8,69-92; tests/tooling/test_framework_adoption.py:895-903 | Restore actual read-input coverage from the Session 30 precedent or narrow the identity claim and specify revalidation for excluded inputs. Include the audit helper and immutable plan contract in the relevant identity. | open |
| F7 | Low / High | no | clerical / committable-tooling | OPENAPI_DIFF allows /api/v1/tts/{job_id}, but the existing route uses /api/v1/tts/{id}. The planned cancel docstring change will be rejected as an unlisted path change. | docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md:140; docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py:76; packages/api/src/avkit_api/routes/tts.py:95-103 | Use /api/v1/tts/{id} consistently in the named allow-list and executable copy; keep the existing route. | open |
| F8 | Low / High | no | clerical / review-scaffolding | check_review compares target_plan with a repository-relative string, whereas this dispatch requires an absolute worktree target and verbatim copying. prereq therefore rejects even an otherwise approved report from this dispatch. | docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py:321-325; docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1:155 | Resolve both target values as paths inside this worktree before comparison. Preserve the report verbatim and retain target/intent validation. | open |

### Materiality and decisive traces

**F1 — cancellation at the terminal write.** The violated subcontracts are AC-77.4/77.5, CANCEL_RULE and Spec 03:477; PR-8 also requires the actual atomicity mechanism. The current _finish_done independently reads and commits Done (services/tts.py:252-264). The plan adds flag checks after WAV/MP3 work but never synchronizes the last check with terminal selection. Concrete permitted interleaving: check false → cancel(id) sets the flag while Generating → _finish_done commits Done → finally clears the flag. The requested cancellation and cleanup disappear. This is a missing behavior contract, not a predicate-format demand.

**F2 — shutdown timeout.** AC-77.9 and the plan's Goal promise shutdown will not leave a Generating job. The proposed wait_idle returns a boolean, but SHUTDOWN_STOP gives no action for False. Current lifespan next unloads the model and disposes the engine (main.py:44-51). TTS MP3 convert uses subprocess.run without a completion timeout (media/adapter.py:237-244,362-374); a synthesis segment also has no ten-second bound. A still-running worker can consequently use torn-down dependencies. BOUNDED_WAIT's five-second fake cannot cover this production branch. Worker registration and shutdown admission also need one synchronization rule so shutdown cannot observe idle between job acceptance and thread registration.

**F3 — audit precondition expires.** AC-77.13 and Spec 03:479 require a running-job cancellation proof. After the initial POST response, destructiveStep awaits a probe, omitted-confirm call, probe, false-confirm call, and probe before confirmed cancellation (plan.ts:243-254). A scheduling delay or faster synthesis can finish the target during that sequence. A boolean Cancelled probe is false for both Generating and Done, concealing the loss of the running precondition until confirmed cancellation has no effect. The stub negative tests only an initially Done response. A longer fixture reduces likelihood but cannot make the step deterministic.

**F4 — concrete stale-audit false-pass.** Audit preparation builds/imports A; a gated source changes to B while the audit runs; validate-task.ps1:326 records B for the first time; WINDOWS_GATE then exercises B; gate-check compares B with B. H1-2/H1-4 can accept A's audit as evidence that B's running cancellation passed. No live mutation was executed during review; this is the static producer/consumer trace. Unlike WINDOWS_GATE, the audit has no before/after identity comparison.

**F5 — mandatory rerun dead end.** First audit: non-pass→pass gives FIXED and writes a pass baseline. H1-8 then requires H1-2 again after a gated correction. computeDelta explicitly maps pass→pass to UNCHANGED (classify.ts:123), while exec_checks.py:361 insists on FIXED. The runner rolls back to its immediate prior baseline, which already says pass. Repeating cannot recover. This is a concrete impossible successful revalidation sequence, not a request for deeper predicate mutations.

**F5 is Medium and non-blocking under Materiality Gate #3.** Its repeated-success refusal is a real retry defect, but it rejects valid evidence rather than false-passing a materially missing deliverable. It should be corrected before execution without contributing to changes_required. **F6 is also non-blocking.** The omitted inputs are real reads of the full gate, but no missing Session 33 product behavior is demonstrated solely by their omission. Record the evidence limitation and fix or narrow the identity claim. **F7/F8 remain Low**: both intended path corrections are trivially inferable. They reject valid work rather than prove a missing product capability.

### Closed-vocabulary classification mapping

The CLOSED vocabulary was read from .agent/context/review-vocabulary.yaml; no new mechanism is invented.

| Finding | Chosen mapping | Why |
|---|---|---|
| F1 | behavior; no mechanism | Planned runtime terminal-state behavior can lose cancellation. |
| F2 | behavior; no mechanism | Planned shutdown behavior can tear down resources before the worker stops. |
| F3 | behavior; no mechanism | Delivered live-audit step can target a finished job and fail on correct product behavior. |
| F4 | control-defeat; task-row-completion-predicate | The predicate accepting H1-2/H1-4 as complete mistakes a post-run tree hash for evidence of the tree actually audited. This defeats task completion evidence. It is neither the review-conduct detector nor a verdict-to-ledger transition. |
| F5 | behavior; no mechanism | The rerun evaluator computes a rejecting result for valid repeated audit success; it is a false-negative execution path, not a bypass. |
| F6 | control-defeat; task-row-completion-predicate | The H1-3/H1-4 completion predicate can accept stale gate evidence after an actual input changes outside its hash set. Same catalogued completion-evidence mechanism as F4, non-blocking here. |
| F7 | clerical; no mechanism | Wrong placeholder spelling in an otherwise evident route allow-list. |
| F8 | clerical; no mechanism | Absolute versus relative spelling of the same review target. |

The refused attempt's post-run-only-fingerprint and incomplete-fingerprint-inputs manoeuvre names are replaced by **task-row-completion-predicate** for F4 and F6. Findings, severities and blocking decisions were independently reassessed, not inherited from ledger acceptance.

## Checklist Results

Manual observations: **observer gpt-6.1-sol**, exit_code **null**, procedures and decisive observations below. Product execution is not_run; a passing plan-local self-test does not prove product behavior.

### Plan Review checklist

| Check | Result | Observed procedure and evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compared all 24 task rows with plan MEU, gate, H1 and H2 sections: 76→78→77; TA changes only in their Green rows. |
| PR-2 Not started | pass | git status/diff, unchecked task table, absent handoffs/baseline.sha/canonical review. |
| PR-3 Task contract completeness | pass | All task rows contain owner, deliverable, exact validation, dependencies, durable output and unchecked status; static verifier reports 24 rows. |
| PR-4 Validation realism | fail | Runner/evaluator trace demonstrates F4 false-pass and F5 retry dead end despite passing verifier self-tests. |
| PR-5 Source-backed planning | pass | Compared FIC source columns with residual Spec, grouping, issue records and existing behavior; 422, live resolver and background error amendments have explicit bases. External research URLs were not fetched under this static-only review. |
| PR-6 Handoff/corrections readiness | pass | Three dated MEU handoffs and rolling review paths explicit. Round 1 has no resubmission census prerequisite. |
| PR-7 Scope discipline / C2 | pass | Deferred MEU-72–75/79 exist in SSOT and grouping. MCP timeout, unload guard, persistent cancel flag and separate output-deletion route exclusions do not omit a required new product feature. Shutdown is covered by F2, not excluded by D-20. |
| PR-8 Reachability, totality, atomicity | fail | Route→worker→adapter→repository and settings→resolver consumers are named and reachable. F1/F2 omit material concurrent-state branches; F3/F4 undermine required live-audit proof. |
| PR-9 Single-statement discipline | pass | Read the saved literal census and named contracts. AC/task references point to governing definitions; no materially ambiguous duplicate set found. Fast-terminal response wording is noted in Q6. |

### Documentation Review checklist

| Check | Result | Observed procedure and evidence |
|---|---|---|
| DR-1 Claim-to-state match | pass | Draft/unstarted status agrees with current worktree; planning verifier claims reproduced. |
| DR-2 Residual old terms | pass | Located synchronous generate, probe latch and old MCP cancel text; replacement contracts and hub edits scheduled. |
| DR-3 Downstream references | partial | Hub, SSOT, OpenAPI and handoffs scheduled; F7/F8 require path corrections. |
| DR-4 Verification robustness | fail | Concrete cancellation, shutdown and audit traces F1–F5 are untested or misclassified. |
| DR-5 Evidence auditability | partial | Exact commands, reports, preserved exits and fresh-report removal exist; F4/F6 limit freshness/binding claims. |
| DR-6 Cross-reference integrity | pass | Later residual contracts explicitly supersede old cached/synchronous wording; row 12 reconciles 02/03/04/05/07. |
| DR-7 Evidence freshness | pass | All three allowed planning commands rerun in this worktree. No implementation counts asserted as measured. |
| DR-8 Completion versus residual risk | pass | Plan remains draft, tasks pending and this review refuses implementation readiness. |

### Information Retrieval and template checks

| Check | Result | Procedure / evidence |
|---|---|---|
| All AC have source labels | pass | Read the three FIC tables and named-contract source columns against canon. |
| Validation cells are exact commands | pass | Read task cells and mapped their check names to runner blocks and evaluator verbs. |
| BUILD_PLAN audit row present | pass | Plan :359-373 and task row 12 enumerate required hub reconciliation. |
| Post-MEU handoff/reflection/metrics rows | pass | Read rows 4/7/11 and H1/H2; three handoffs, reflection, issue closure and metrics scheduled. |
| Naming convention and template version | pass | Compared dated paths and frontmatter with REVIEW-TEMPLATE 2.2 and user-required nine-key frontmatter. |
| YAML frontmatter | pass | Manual nine-key/value comparison; no Recheck heading in this Round 1 artifact. |
| Execution evidence bundle / FAIL_TO_PASS table | n/a | Unstarted plan: these remain execution deliverables. |
| Commands independently runnable | partial | Three permitted commands passed; other scripts exist and were read, but execution prohibited. F5/F7/F8 require correction. |
| Completed-product anti-placeholder scan | n/a | No completed implementation under review. |

### Reviewer adversarial checks

| Check | Result | Procedure / evidence |
|---|---|---|
| AV-1 Failing-then-passing / AV-3 assertion coverage | partial | Red design ties assertions to named ACs; runtime evidence does not exist yet. Add terminal-race/timeout/precondition-expiry cases for F1–F3. |
| AV-2 No bypass hacks / AV-4 no skip masking | pass | Plan forbids test neutralization; Red rejects tagged skipped/error/flaky outcomes and requires decisive failures, with explicit negative-only and pin exceptions. |
| AV-5 No unresolved completed placeholders | n/a | No completed deliverable claim. |
| AV-6 Source-backed criteria | pass | Compared source labels and residual Spec as PR-5. |

### Required sweep dispositions

1. **Plan-task consistency:** all 24 rows align; TA changes are Green-only.
2. **Status readiness:** unstarted, confirmed by Git and missing execution artifacts.
3. **Role/ownership:** each task contract has its required fields.
4. **Validation specificity:** read exact runner argv and report evaluators, not only command labels; F4/F5 remain.
5. **Dependencies/order:** coherent, acyclic 76→78→77; shared-file snapshot handoff checked in Q2.
6. **Source traceability:** residual Spec, grouping, SSOT issues and old tests compared.
7. **Scope discipline:** deferred IDs exist; no material hidden deferral found.
8. **Referenced-artifact existence:** 15 named runner/config/template/script dependencies sampled with Test-Path all True; static verifier checks every Files Modified target. New AC test files are explicitly scheduled create rows. Missing handoffs/baseline.sha are expected before execution.
9. **Repeated literals:** untruncated receipt s33-rerun-literal-census.txt inventories Generating/Cancelled/wait/resolver/Red/fingerprint references; manually compared governing definitions with usages. F7/F8 are path-spelling defects, not competing behavioral definitions.

## Answers to Q1–Q9

### Q1 — TEST_AMENDMENTS

**This verdict individually approves TA-1, TA-2, TA-3, TA-4, TA-5, TA-6, TA-7, TA-8, TA-9 and TA-10**, only as specified by TEST_AMENDMENTS. Overall plan approval and execution authorization are withheld. No additional expectation change is approved.

| TA | Approval and minimal source-backed change |
|---|---|
| TA-1 | Approved. Add ExtractError to the closed error inventory (test_domain.py:181-217); Spec 04:437 requires the new typed domain error. Preserve distinctness/order checks. |
| TA-2 | Approved. Count two absent-binary resolutions instead of one (test_filesystem_media.py:254-258), because later Spec 03:492 supersedes 02:428's latch. Preserve configured/bundle/PATH ordering assertions; keep ffprobe fixture setup from contaminating the ffmpeg-only counter. |
| TA-3 | Approved. Add ffmpeg_binaries to test_domain.py:1153's MediaPort method inventory; FFMPEG_BINARIES implements Spec 03:491-493. |
| TA-4 | Approved. Add the same method to test_filesystem_media.py:196's adapter/port inventory. |
| TA-5 | Approved. Add list_by_status to test_domain.py:1407's TTS repository tuple; RESTART_RECOVERY needs the sourced startup recovery query. |
| TA-6 | Approved. Add list_by_status to test_sqlite_uow.py:313's repository tuple; preserve all existing persistence assertions. |
| TA-7 | Approved. Only the final invalid-progress block at test_services.py:1767-1778 changes from raises to eventual Failed after an asserted bounded idle wait. Earlier progress and cancellation assertions remain. Later Spec 03:476 and WORKER_RULE replace inline propagation. |
| TA-8 | Approved. Remove the invalid-progress re-raise expectation at :2064-2073, wait boundedly and keep its existing one-row/Failed assertions (:2074-2076). Same background-worker source. |
| TA-9 | Approved. The two unexpected worker-error POSTs at test_tts_assets.py:633,639 become 201, then wait/read eventual Failed. Preserve both messages, including the empty RuntimeError message case and proof ownership clears. Spec 03:423's message requirement remains; 03:476/D-19 replace only the synchronous 500. |
| TA-10 | Approved. For the two HTTP-based cases :696-722, read Done/error/output via GET after bounded idle rather than expecting the original POST snapshot to mutate. Preserve real ONNX execution and decoded clipped-sample assertions. The third similarly named AC-62.16 case at :796 directly calls the adapter and is outside this amendment. |

FIXTURE_REPAIRS do not authorize weakening assertions. A synchronous spawn in the old service fixture preserves existing synchronous test observations; new threaded tests still use the real default spawn. Every wait must be asserted as BOUNDED_WAIT requires.

**Marker fence: present, but file-level only.** TA_SITES identifies all ten expected files; api-scope checks each TA-n (Session 33 substring and rejects a TA marker in the wrong changed test file (exec_checks.py:560-568). It does not prove comment adjacency, minimal diffs or that no other assertion changed. Human/independent diff review and row-1 census/S2 remain necessary. Do not claim the marker alone is an assertion-level fence.

### Q2 — Red proof and snapshots

The designed Red pipeline is substantially sound. red76 first compares its product files with baseline.sha. gate76 snapshots the union of every MEU's product paths only on success; red78 compares its paths to that snapshot. gate78 writes a new union snapshot only on success; red77 compares against that later snapshot (exec_checks.py:607-644; runner :196-250). This correctly preserves MEU-76 edits to health/youtube and MEU-78 edits to wiring instead of treating them as premature edits for the next MEU.

RED_RULE/evaluate_red requires at least one decisive assertion failure for every non-pin AC in its tier, rejects ordinary tagged passes, tagged skips/errors/flaky results, load/collection failures and untagged failures. AC-77.14 must pass in its pin-only Electron run with exit 0. It pins existing renderer behavior, not a nonexistent GUI regression.

**Collection/import errors and tagged skips cannot stand in for Red; representative load, TypeError and runner-timeout cases are rejected by the self-test.** A process that times out before producing its fresh report fails rather than reusing a stale file. Playwright locator expect failures are assertion failures; a runner test timeout is not.

The classifier is message-based, so it cannot establish why an AssertionError happened: an asserted fake Event.wait timeout can resemble a product assertion. Inspect the saved traceback and ensure the unchanged synchronous product returns after the fake's bounded release, then fails on the intended status/latency observation. Guards cover listed MEU product files, not every dependency. No actual MEU Red has been executed or certified in this review.

### Q3 — CORS_SAFE_500 and ERROR_EVENT

**Yes for ordinary route/service exceptions before response headers are sent, as a static design conclusion.** main.py registers CORSMiddleware after request_id_middleware, so CORS wraps the latter. Catching call_next there turns the exception into a normal masked JSON response that returns through CORS. Log once at that conversion, set the same id in body/header, unbind context in finally and return without re-raising.

Mapped DomainError, RequestValidationError and HTTPException handlers run inside that middleware and return normally; their statuses, masking rules, envelope text and HTTPException headers can remain unchanged. Unmapped DomainError needs its own once-only event because its inner handler already consumed the exception. Mapped 503s remain masked and emit no api.unhandled_error. Tests AC-76.1/2/4 cover the principal positive/negative paths.

A catch cannot retroactively replace a response after streaming has started, nor wrap failures outside its layer. No new streaming route is planned. No runtime middleware probe was permitted here.

### Q4 — EXTRACT_STATUS

**422 is a reasonable, source-backed plan-time choice.** Spec 04:437 explicitly delegates the status choice; AgeRestrictedError and CookieTestError are existing 422 precedents. The expected user-actionable extraction refusal should preserve its message rather than enter the masked 500 branch. This is a local contract judgment, not a claim every upstream outage intrinsically means 422.

The three _run_extract sites are centralized (adapter.py:393/395/397). Both extract_info and extract_video_ids use it; download add calls extract_info, transcript add calls both coordinator methods (:129-130). ExtractCoordinator uses try/finally and does not translate the error. AC-76.6 covers adapter classification; AC-76.7 covers both HTTP entrypoints. At execution, parameterize transcript failure at both metadata and ID extraction so a late ID-extraction failure is covered. Age-gate classification and download()'s plain DomainError job-failure behavior stay as specified.

### Q5 — resolver order and live source

**Removing the latch is consistent with later Spec 03:492.** D-16 resolves the old 02:428 conflict expressly and row 12 reconciles that canon. Existing wiring shares one MediaPort among Convert, TTS MP3 and health; moving construction before YouTube and injecting a callable provides the fourth consumer. Every media entrypoint must use ffmpeg_binaries via its resolver/require path; settings are read through LIVE_SOURCE, not a captured startup value.

The path-keyed GPU capability cache is allowed: it caches expensive capabilities, not binary selection, and the plan requires a re-probe when the path changes. Health must report the resolver's output and yt-dlp must call its location source for each options construction. FFprobe sibling/PATH behavior and settings/card invalidation have explicit tests.

No replacement implementation exists yet to certify. Passing the parent directory assumes conventional ffmpeg/ffprobe filenames; a renamed executable would require its exact path or a naming constraint. That is a non-blocking edge observation under this plan's stated conventional fixtures.

### Q6 — async lifecycle, cancellation, cleanup and bounded waits

**Not yet sound; F1 and F2 block.** Creation under _lock preserves one-at-a-time admission, but final cancellation/terminal selection and shutdown/worker registration need a complete atomic protocol. Shutdown must stop admitting work before it decides all workers are idle.

_current_id clears on the stated normal worker finally path and spawn-failure path. It is not justified to say it always clears: an active worker can outlast shutdown, and recording failure/cleanup can itself raise. Cleanup/ownership finalization must execute even if terminal persistence fails, under the same synchronization, and only for the owning job. Do not report idle while a worker still uses model/database resources.

PARTIAL_CLEANUP covers WAV and MP3 on normal failed/cancelled paths. Its explicit logged-and-ignored unlink OSError is an operational exception to absolute “no partial output” wording; keep the diagnostic and report the residual. RESTART_RECOVERY/list_by_status is appropriate, and its entered TestClient lifespan test avoids the existing non-entered Stack.client trap.

D-24 returns the current stored row, so a very fast/default worker or synchronous test spawn may already yield Done/Failed. That is compatible with prompt return, although unconditional Generating prose should acknowledge it. Gated-port tests can reliably observe Generating.

BOUNDED_WAIT bounds explicit fake/test waits, not arbitrary product deadlocks or external synthesis/subprocess calls. It does not prove every threaded test is hang-proof. gate77's five pytest runs have distinct receipts; Electron repeat-each=5 is meaningful sampling. Neither reliably covers a missing final-commit interleaving or timeout branch; deterministic barriers/controlled results are required for F1/F2.

### Q7 — fingerprints with no commit or clean-tree gate

**A content fingerprint can bind an uncommitted tree without a clean-tree requirement.** The implementation hashes sorted path/content pairs, deletion markers and untracked non-ignored files relative to baseline.sha. Windows before/after equality plus later current-tree recomputation detects ordinary persistent edits within GATED_PATHS.

**Audit binding is insufficient: F4 hashes only after the work.** F6 also limits the “all inputs” claim. An edit to any of these can escape the identity:

- Older layout plan or grouping read by layout-canon.
- .agent/workflows/mcp-audit.md and workflow/skill index READMEs read by audit/docs.
- .agent/docs/commands.md and docs/execution/plans/TASK-TEMPLATE.md read by tooling tests.
- This plan's implementation-plan.md, plan_checks.py and baseline_carry.py.
- The expressly excluded SSOT/status/known-issues/handoff/reflection/BUILD_PLAN closeout files.

Post-review doc-suite reruns address the stated closeout policy, not all other omitted inputs. Session 30 explicitly covered several omitted homes. Recorded Node/Electron/external-input values also are not independently remeasured by gate-check; do not infer current environment equality from their presence in JSON. A temporary edit reverted between the before/after measurements is outside what endpoint hashing detects. Final review must independently compare the current intended identity.

### Q8 — deterministic audit and baseline carry

**The running-job step is not deterministic (F3), and a successful audit cannot be rerun as required (F5).** Requiring actual Cancelled in the probe is otherwise correct: a no-op DELETE against Done cannot satisfy it.

**--update-baseline followed by baseline_carry.py follows BASELINE_ANNOTATION_RULE at the JSON-content level.** The audit alone writes statuses/findings/timestamps. Carry copies only prior issue fields for identical tool/action/status entries or code/tool findings; missing issue ids refuse before writing. It now refuses an absent/unchanged recorded_at, allowing distinct runs at one uncommitted HEAD without using recorded_commit as the only freshness test. This guard is not independent provenance authentication.

Under AUDIT_EXPECT all entries pass and no findings remain, so carry changes no semantic fields. Wrapper rollback restores the prior baseline after audit, carry or expectation failure and retains diagnostics. Fix F5 with immutable comparison evidence or explicit linked revalidation, never by fabricating a baseline/delta.

### Q9 — product and OpenAPI scope

**api-scope catches out-of-scope files at its documented file boundary.** It compares tracked/untracked changes with Files Modified and census-listed fake repairs, freezes tools and ui/src/main, requires scheduled created files, and rejects unlisted API files or package manifest edits. It does not constrain unrelated edits inside allowed files or verify that a census “repair” preserves assertions. Independent diff review remains required.

openapi_diff catches added/removed paths, changed unlisted paths, changed/added/removed unlisted component schemas, and unrelated top-level metadata changes. **Correct F7's /{job_id} to the existing /{id}.** The allow-list is schema/path-level, not a field-level restriction within listed schemas.

Non-schema components such as components.securitySchemes are not compared: the helper checks schemas then omits the entire components object from its rest comparison. No auth-component edit is required by this plan; inspect the complete generated diff and preserve existing auth. No generator was run here.

## Commands Executed and Output

Every shell operation used cwd **P:/av-kit-wt/backend-robustness** and an RTK route. Canonical receipt form was:

```powershell
$env:RECEIPTS_DIR='C:/Temp/av-kit'
rtk proxy <command> *> C:/Temp/av-kit/<receipt>.txt
$s33Exit=$LASTEXITCODE
rtk proxy pwsh -NoProfile -Command 'Get-Content C:/Temp/av-kit/<receipt>.txt'
exit $s33Exit
```

### Permitted verifier commands — fresh complete output

Each command below exited **0** in this re-run. Expected FAIL lines inside self-tests are successful negative cases, not failed verifier commands.

```text
$ rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static
PASS static: 24 task rows; script, exec_checks, plan contracts, references and file targets agree

$ rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py selftest
PASS selftest duplicate row id: duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6',
PASS selftest unknown check: task.md invokes -Check 'no-such-check', which validate-task.ps1 does not define
PASS selftest swapped stage: stage order differs: ps1=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-bui
PASS selftest gated path dropped: GATED_PATHS differ: plan=['ui', 'packages', 'mcp-server', 'tests', 'tools', 'pyproject.toml', 'uv.lock', 'openapi.committed.json', 'docs/bui
PASS selftest changed floor: COUNT_FLOORS differ: plan={'pytest': 600, 'vitest': 773, 'e2e': 133} exec_checks={'pytest': 655, 'vitest': 773, 'e2e': 133}
PASS selftest AC tier changed: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'
PASS selftest AC row dropped: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'
PASS selftest pin dropped: pins differ: plan=set() exec_checks={'77.14'}
PASS selftest TA file changed: TEST_AMENDMENTS differ: plan={1: 'tests/unit/test_domain.py', 2: 'tests/integration/test_filesystem_media.py', 3: 'tests/unit/test_domain.py
PASS selftest source audit file dropped: $SRC76 differs from product_files: ps1-only={'x.ts'} plan-only={'ui/src/renderer/src/lib/api.ts'}
PASS selftest red without guard: red78 does not start with the red-guard
PASS selftest TA in red: red77 runs a TEST_AMENDMENTS array (TAs apply only in Green)
PASS selftest undefined AC: task.md references AC-78.99, which has no definition site
PASS selftest undefined D: task.md references D-99, which has no definition site
PASS selftest undefined TA: task.md references TA-11, which has no definition site
PASS selftest missing modify target: Files Modified 'modify' row names a missing file: ui/no/such/file.ts
PASS selftest existing create target: Files Modified 'create' row names a file that already exists: pyproject.toml
PASS selftest missing goal anchor: review-prompt-plan.md does not contain the Goal sentence (INTENT_BINDING)
PASS selftest: every injected defect was reported

$ rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py selftest
ok  pytest red76 good: PASS (expected PASS)
  ok  pytest red76 with a NEG_MARK pass: PASS (expected PASS)
  ok  pytest red76 TypeError (non-assertion): FAIL (expected FAIL) - non-assertion failure: tests.unit.test_x::test_ac_76_7_x: TypeError: unexpected keyword 's
  ok  pytest red76 missing AC-76.7: FAIL (expected FAIL) - AC-76.7 has no decisive assertion failure in pytest
  ok  pytest red76 tagged pass without NEG_MARK: FAIL (expected FAIL) - tagged test passed in Red (no NEG_MARK): tests.unit.test_x::test_ac_76_1_extra
  ok  pytest red76 untagged failure: FAIL (expected FAIL) - untagged test did not pass (failed): tests.unit.test_x::test_old_breaks
  ok  pytest red76 collection error: FAIL (expected FAIL) - collection error ::tests.unit.test_x: ImportError: x
  ok  pytest red76 ac_76_10 is not AC-76.1: FAIL (expected FAIL) - tests.unit.test_x::test_ac_76_10_x: AC-76.10 is not an AC of MEU-76
  ok  pytest red76 exit 0: FAIL (expected FAIL) - Red run exited 0
  ok  pytest red76 DID NOT RAISE counts: PASS (expected PASS)
  ok  vitest red76 good: PASS (expected PASS)
  ok  vitest red76 load error: FAIL (expected FAIL) - load error x.test.ts: Failed to resolve import
  ok  vitest red76 TypeError: FAIL (expected FAIL) - non-assertion failure: api AC-76.8 x: TypeError: Cannot read properties of undefined
  ok  vitest red76 AC-76.80 not AC-76.8: FAIL (expected FAIL) - AC-76.80 x: AC-76.80 is not an AC of MEU-76
  ok  mcp red76 jest-dom style expect: PASS (expected PASS)
  ok  electron red78 good: PASS (expected PASS)
  ok  electron red78 test timeout: FAIL (expected FAIL) - non-assertion failure: f.ts > AC-78.9 x: Test timeout of 30000ms exceeded.
  ok  electron red78 top-level error: FAIL (expected FAIL) - top-level error: Error: launch failed
  ok  electron red77 pin passes: PASS (expected PASS)
  ok  electron red77 pin fails: FAIL (expected FAIL) - pin test must pass in Red (failed): f.ts > AC-77.14 x
  ok  electron red77 pin flaky: FAIL (expected FAIL) - pin test must pass in Red (flaky): f.ts > AC-77.14 x
  ok  pytest green77 needs every AC: FAIL (expected FAIL) - AC-77.10 has no passing test in pytest
  ok  pytest green77 good: PASS (expected PASS)
  ok  pytest green77 a failure: FAIL (expected FAIL) - exit 1
  ok  fingerprint lines sorted, content-bound, deletions recorded
  ok  openapi allowed change: PASS
  ok  openapi added path: FAIL
  ok  openapi other schema: FAIL
  ok  openapi other path: FAIL
  ok  audit good: PASS
  ok  audit cancel not FIXED: FAIL
  ok  audit regression: FAIL
  ok  audit cleanup failed: FAIL
  ok  audit baseline misses an action: FAIL
  ok  audit baseline commit drift: FAIL
  ok  gate good: PASS
  ok  gate tree changed after: FAIL
  ok  gate stage order: FAIL
  ok  gate e2e flaky: FAIL
  ok  gate pytest under carried floor: FAIL
  ok  gate mcp under row-0 floor: FAIL
  ok  gate fingerprint moved in run: FAIL
  ok  review good: PASS
  ok  review self-authored agent: FAIL
  ok  review changes_required: FAIL
  ok  review over cap: FAIL
PASS selftest
```

The bounded diagnostic endings above are printed by the verifiers themselves. Full stdout is embedded, rather than only a receipt link.

### Static reads and sweeps — commands/procedures and decisive output

| Actual command / read procedure | Exit | Decisive observation |
|---|---|---|
| rtk proxy git status --short --branch | 0 | ## claude/backend-robustness; ?? docs/execution/plans/2026-10-14-backend-robustness/. Two warnings: unable to access C:\\Users\\Mat/.config/git/ignore, Permission denied. |
| rtk proxy git diff --stat | 0 | Empty output: no tracked changes. |
| rtk proxy git log -1 --format=%H | 0 | 78610200ea2e7efd52318ea95c3e48b6df4993ba. |
| rtk proxy rg -n '^' docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 | 0 | Read all 512 runner lines; Red guard :197/220/245; audit post-only fingerprint :326; Windows before/after :344/449. |
| rtk proxy rg -n '^' on plan_checks.py and baseline_carry.py; rtk proxy pwsh Get-Content ranges on exec_checks.py | 0 | Read static/evaluator code and carry rules. check_audit :361 requires FIXED; red-guard :625-644 compares content; api-scope :540-574 checks files/markers/OpenAPI. |
| rtk proxy pwsh -NoProfile -Command Get-Content reads of protocol, AGENTS, GUARDRAILS, PROFILE, REVIEW-TEMPLATE, reviewer role, harness/focus/known-issues, terminal/output policy, completion-preflight, vocabulary and verdict schema | 0, except incidental diagnostic below | Protocol and template 2.2 loaded; vocabulary contains only task-row-completion-predicate, verdict-to-state-transition and review-conduct-detection. No contents treated as user approval. |
| rtk proxy pwsh bounded Get-Content reads of named build-plan/grouping/source/test files | 0 | Spec 03:476-479 and 04:435-438; existing latch and synchronous service; inner HTTP/domain mapping; shared media wiring; audit awaited-call sequence; all ten expectation sites. Current DELETE route uses /{id}. |
| rtk proxy rg -n -A 27 'id: (API-UNHANDLED-ERROR-OPAQUE\|FFMPEG-RESOLUTION-DIVERGENCE\|MCP-TTS-GENERATE-SYNCHRONOUS)' .agent/context/known-issues.yaml | 0 | All three issues open; residual causes match proposed scope. |
| rtk proxy rg -n -A 7 'id: MEU-(72\|73\|74\|75\|76\|77\|78\|79)' .agent/context/meu-status.yaml | 0 | All deferred/target MEU ids exist (:1909,1935,1959,1985,2010,2034,2062,2088). |
| rtk proxy rg -n call/read-input patterns on health/repositories/extract/download/transcript, layout-canon, audit/docs, tooling tests and Session 30 plan | 0 | Real omitted inputs confirmed: layout-canon :15-19; audit/docs :8,91-92; tooling :895/903. Session 30 :174 fingerprints those homes. |
| rtk proxy rg -n -e 'Generating\|Cancelled\|wait_idle\|ffmpeg_location\|RED_RULE\|GATE_FINGERPRINT\|AUDIT_FINGERPRINT\|FIXED' on implementation-plan.md and task.md | 0 | Literal census retained untruncated in its receipt; named definitions and references crosschecked. The backslashes before pipe characters here escape Markdown table separators; the executed regular expression uses plain alternation pipes. |
| rtk proxy pwsh Test-Path loop for 15 runner/config/template dependencies and five expected-unstarted artifacts | 0 | All 15 dependencies True. Three handoffs, canonical review and baseline.sha False. |
| Session 30 plan/baseline helper/peer review reads | 0 | Prior plan's GATED_PATHS includes actual doc-reading dependencies. Prior helper uses issue-only carry; Session 33 adds unchanged-recorded_at refusal and automatic rollback. |
| Final task/workflow Get-Content reread; report Get-Content/Get-Item readback; report heading/finding rg; final git status --short --branch | 0 each | All 24 task rows still unchecked; report exists and is readable; all Q1–Q9 headings and eight finding rows present; final status unchanged with only the untracked Session 33 plan directory. |

Incidental reviewer shell problems were preserved and not attributed to the plan: the initial contract read interpolated an environment assignment in its outer string, printed “term ... is not recognized” but the subsequent file reads completed and pwsh exited 0; the assignment was corrected in the verifier processes. A range-helper named R collided with PowerShell's Invoke-History alias (exit 1); renaming the helper produced the successful canon read. One oversized read command returned exit 1 with an empty receipt and was replaced by successful smaller reads. None ran a target validator/product command or wrote the repository.

### Durable evidence

```json
{"schema_version":"evidence.v1","check_id":"s33-plan-static","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static","cwd":"P:/av-kit-wt/backend-robustness","scope":"Plan-local static verifier","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba; tracked diff empty; unstarted Session 33 plan directory untracked","output":"PASS static: 24 task rows; script, exec_checks, plan contracts, references and file targets agree","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-plan-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py selftest","cwd":"P:/av-kit-wt/backend-robustness","scope":"Plan-local static negative cases","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba; tracked diff empty; unstarted Session 33 plan directory untracked","output":"PASS selftest duplicate row id: duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6',\r\nPASS selftest unknown check: task.md invokes -Check 'no-such-check', which validate-task.ps1 does not define\r\nPASS selftest swapped stage: stage order differs: ps1=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-bui\r\nPASS selftest gated path dropped: GATED_PATHS differ: plan=['ui', 'packages', 'mcp-server', 'tests', 'tools', 'pyproject.toml', 'uv.lock', 'openapi.committed.json', 'docs/bui\r\nPASS selftest changed floor: COUNT_FLOORS differ: plan={'pytest': 600, 'vitest': 773, 'e2e': 133} exec_checks={'pytest': 655, 'vitest': 773, 'e2e': 133}\r\nPASS selftest AC tier changed: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'\r\nPASS selftest AC row dropped: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'\r\nPASS selftest pin dropped: pins differ: plan=set() exec_checks={'77.14'}\r\nPASS selftest TA file changed: TEST_AMENDMENTS differ: plan={1: 'tests/unit/test_domain.py', 2: 'tests/integration/test_filesystem_media.py', 3: 'tests/unit/test_domain.py\r\nPASS selftest source audit file dropped: $SRC76 differs from product_files: ps1-only={'x.ts'} plan-only={'ui/src/renderer/src/lib/api.ts'}\r\nPASS selftest red without guard: red78 does not start with the red-guard\r\nPASS selftest TA in red: red77 runs a TEST_AMENDMENTS array (TAs apply only in Green)\r\nPASS selftest undefined AC: task.md references AC-78.99, which has no definition site\r\nPASS selftest undefined D: task.md references D-99, which has no definition site\r\nPASS selftest undefined TA: task.md references TA-11, which has no definition site\r\nPASS selftest missing modify target: Files Modified 'modify' row names a missing file: ui/no/such/file.ts\r\nPASS selftest existing create target: Files Modified 'create' row names a file that already exists: pyproject.toml\r\nPASS selftest missing goal anchor: review-prompt-plan.md does not contain the Goal sentence (INTENT_BINDING)\r\nPASS selftest: every injected defect was reported","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-exec-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py selftest","cwd":"P:/av-kit-wt/backend-robustness","scope":"Receipt evaluator self-test","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba; tracked diff empty; unstarted Session 33 plan directory untracked","output":"ok  pytest red76 good: PASS (expected PASS)\r\n  ok  pytest red76 with a NEG_MARK pass: PASS (expected PASS)\r\n  ok  pytest red76 TypeError (non-assertion): FAIL (expected FAIL) - non-assertion failure: tests.unit.test_x::test_ac_76_7_x: TypeError: unexpected keyword 's\r\n  ok  pytest red76 missing AC-76.7: FAIL (expected FAIL) - AC-76.7 has no decisive assertion failure in pytest\r\n  ok  pytest red76 tagged pass without NEG_MARK: FAIL (expected FAIL) - tagged test passed in Red (no NEG_MARK): tests.unit.test_x::test_ac_76_1_extra\r\n  ok  pytest red76 untagged failure: FAIL (expected FAIL) - untagged test did not pass (failed): tests.unit.test_x::test_old_breaks\r\n  ok  pytest red76 collection error: FAIL (expected FAIL) - collection error ::tests.unit.test_x: ImportError: x\r\n  ok  pytest red76 ac_76_10 is not AC-76.1: FAIL (expected FAIL) - tests.unit.test_x::test_ac_76_10_x: AC-76.10 is not an AC of MEU-76\r\n  ok  pytest red76 exit 0: FAIL (expected FAIL) - Red run exited 0\r\n  ok  pytest red76 DID NOT RAISE counts: PASS (expected PASS)\r\n  ok  vitest red76 good: PASS (expected PASS)\r\n  ok  vitest red76 load error: FAIL (expected FAIL) - load error x.test.ts: Failed to resolve import\r\n  ok  vitest red76 TypeError: FAIL (expected FAIL) - non-assertion failure: api AC-76.8 x: TypeError: Cannot read properties of undefined\r\n  ok  vitest red76 AC-76.80 not AC-76.8: FAIL (expected FAIL) - AC-76.80 x: AC-76.80 is not an AC of MEU-76\r\n  ok  mcp red76 jest-dom style expect: PASS (expected PASS)\r\n  ok  electron red78 good: PASS (expected PASS)\r\n  ok  electron red78 test timeout: FAIL (expected FAIL) - non-assertion failure: f.ts > AC-78.9 x: Test timeout of 30000ms exceeded.\r\n  ok  electron red78 top-level error: FAIL (expected FAIL) - top-level error: Error: launch failed\r\n  ok  electron red77 pin passes: PASS (expected PASS)\r\n  ok  electron red77 pin fails: FAIL (expected FAIL) - pin test must pass in Red (failed): f.ts > AC-77.14 x\r\n  ok  electron red77 pin flaky: FAIL (expected FAIL) - pin test must pass in Red (flaky): f.ts > AC-77.14 x\r\n  ok  pytest green77 needs every AC: FAIL (expected FAIL) - AC-77.10 has no passing test in pytest\r\n  ok  pytest green77 good: PASS (expected PASS)\r\n  ok  pytest green77 a failure: FAIL (expected FAIL) - exit 1\r\n  ok  fingerprint lines sorted, content-bound, deletions recorded\r\n  ok  openapi allowed change: PASS\r\n  ok  openapi added path: FAIL\r\n  ok  openapi other schema: FAIL\r\n  ok  openapi other path: FAIL\r\n  ok  audit good: PASS\r\n  ok  audit cancel not FIXED: FAIL\r\n  ok  audit regression: FAIL\r\n  ok  audit cleanup failed: FAIL\r\n  ok  audit baseline misses an action: FAIL\r\n  ok  audit baseline commit drift: FAIL\r\n  ok  gate good: PASS\r\n  ok  gate tree changed after: FAIL\r\n  ok  gate stage order: FAIL\r\n  ok  gate e2e flaky: FAIL\r\n  ok  gate pytest under carried floor: FAIL\r\n  ok  gate mcp under row-0 floor: FAIL\r\n  ok  gate fingerprint moved in run: FAIL\r\n  ok  review good: PASS\r\n  ok  review self-authored agent: FAIL\r\n  ok  review changes_required: FAIL\r\n  ok  review over cap: FAIL\r\nPASS selftest","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-static-adversarial-traces","procedure":"Read the named plan contracts, current production callers, runner, evaluator, audit step and delta classifier; enumerate the interleavings and rerun sequence in F1-F5.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/backend-robustness","scope":"planned cancellation/shutdown and required audit proof","phase":"planning","exit_code":null,"result":"fail","tested_state":"unstarted Session 33 plan at HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba; tracked diff empty","output":"F1-F5 remain open: cancellation may lose terminal race; shutdown ignores False; audit running precondition may expire; audit hash is post-only; repeated successful audit yields rejected UNCHANGED.","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-product-execution","procedure":"No product tests, builds, generators, validate-task checks or MCP audit invoked, per explicit user restriction.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/backend-robustness","scope":"product execution","phase":"planning","exit_code":null,"result":"not_run","tested_state":"unstarted plan","output":"Planning verifier passes establish their own checks only; no product execution evidence claimed."}
```

No additional structural verifier was run. Report frontmatter/required sections and final JSON field shapes were manually compared with the supplied template, vocabulary and review-verdict.schema.v2.json. The report's findings table is generated from the same eight finding records as the final JSON.

## Open Questions and Residual Risk

No new human product decision is needed to correct F1–F5: choose and document safe synchronization/timeout handling and a repeatable identity-bound audit within the existing intent. The exact ten amendments do not authorize other expectation changes.

Real Red/Green receipts, middleware behavior, Electron runtime behavior and authoritative model/network audit remain unmeasured until execution is authorized. Marker presence and assertion-message classification do not establish semantic correctness; endpoint fingerprints have the limits in Q7, and OpenAPI scope has the limit in Q9. Do not fabricate successful unlink cleanup when the filesystem refuses it.

## Verdict

**changes_required** — the plan substantially covers MEU-76/MEU-78 and MEU-77's intended call chain, but F1–F4 leave cancellation/shutdown behavior and its mandatory audit proof insufficient. **Intent achieved: partial** at plan level.

TA-1 through TA-10 are each approved within Q1's exact scope. F5/F6 are Medium and non-blocking, and F7/F8 are Low clerical corrections. The three passing plan-local verifiers do not override the four blocking findings.

## Follow-Up Actions

1. Resolve F1–F5 through /plan-corrections; preserve this independent report.
2. Specify terminal-cancel atomicity and shutdown timeout/admission rules, then add bounded deterministic test designs.
3. Handle audit running-precondition loss, bind its full execution interval to the tree, and allow repeat successful audits without hand-editing statuses or baselines.
4. Address F6's input coverage claim and correct F7/F8 in the consumers, not in this report.
5. Rerun the three planning verifiers after correction. Round 2 must supply an untruncated blast-radius census and per-hit dispositions under PR-6; continue the same loop.
6. Dispatcher copies this receipt verbatim to the canonical rolling review path. This reviewer does not chain into implementation or corrections.

Report: **C:/Temp/av-kit/dispatch/s33-plan-review-report.md**

Canonical destination (dispatcher-owned): **P:/av-kit-wt/backend-robustness/.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md**

---

## Corrections Applied (2026-10-15)

> **Author:** Claude Code (plan author, coder role, running /plan-corrections). This section does not change the round 1 verdict above. The `changes_required` verdict, its findings and its Q1–Q9 answers stand as the reviewer wrote them. Plan-corrections Step 6 changes the frontmatter `verdict:` to `corrections_applied` to show the plan is ready for re-review. Only an independent `/plan-critical-review` round may set `approved`.

### Plan summary

The goal and the order are unchanged: MEU-76 `api-error-surface`, then MEU-78 `svc-ffmpeg-resolver`, then MEU-77 `svc-tts-async-generate`. The corrections make the TTS cancel, worker and shutdown paths linearize under one lock and fail closed on a stop timeout. They make the live-audit cancel step retry when the job finishes too early, and every audit attempt compares against the pre-session baseline. The audit and gate fingerprints now cover the whole tree minus a named exclusion list, measured before and after the audit.

### Findings and dispositions

| Finding | Disposition | Where |
|---|---|---|
| F1 (High, behavior): cancel was not atomic with the worker's terminal write | **Fixed (D-25).** `_lock` linearizes `cancel` and the terminal write. The worker reaches exactly one outcome, and `_finish` runs exactly once in `finally`, deciding and writing under the lock and clearing `_current_id` and the flag. AC-77.5 (b) adds a barrier test that cancels between the final check and the terminal commit. | `CANCEL_RULE`, `WORKER_RULE`, `ASYNC_GENERATE`; AC-77.5 (a)-(b); D-25 |
| F2 (High, behavior): shutdown ignored `wait_idle` returning False | **Fixed (D-26).** `stop_processing(timeout: float = 10.0) -> bool`. It sets `_closing` (new runs get a `ConflictError` / 409 in the same critical section), and the lifespan skips `models.unload` and `engine_dispose` when it returns `False`, logging `api.shutdown_tts_busy`. AC-77.9 (a)-(d) tests the timeout branch with a controlled wait result. | `SHUTDOWN_STOP`, `ASYNC_GENERATE`, `FIXTURE_REPAIRS` (e); AC-77.9; `main.py` row; D-26 |
| F3 (High, behavior): the audit cancel step could target a finished job | **Fixed (D-27).** `destructiveStep` gains `raceLost` and `attempts` (default 1). For `tts.cancel` the precondition reads `tts_job2` as Generating, `reestablish` POSTs a new job, `raceLost` is a `Done` terminal and `attempts` is 3; the step passes only on an actual `Cancelled` result. | `AUDIT_CANCEL_STEP`; AC-77.13 (a)-(d); `plan.ts` row; D-27 |
| F4 (High, control-defeat, `task-row-completion-predicate`): the audit fingerprint was measured only after the run | **Fixed (D-29).** `-Check audit` fingerprints before the prep (excluding only the generated baseline) and after the carry. The `audit-fp` verb writes `audit-fingerprint.json {before, after}`, and `gate-check` (`check_audit_fp`) requires before == after == the current tree. | `AUDIT_FINGERPRINT`; `exec_checks.py` `audit-fp`, `check_audit_fp`; `validate-task.ps1` audit block; D-29 |
| F5 (Medium, behavior): a rerun reported UNCHANGED, not FIXED | **Fixed (D-28).** New `AUDIT_COMPARISON`: every attempt restores the pre-session baseline byte for byte from `git show <baseline.sha>:<baseline>` and runs `baseline_carry.py` against it. A failure restores the start-of-check copy and deletes the attempt's plan-folder evidence. | `AUDIT_COMPARISON`; `validate-task.ps1` `AuditFail`; D-28 |
| F6 (Medium, control-defeat, `task-row-completion-predicate`): `GATED_PATHS` omitted real gate inputs | **Redesigned (D-29).** `GATED_PATHS` is now the whole tree minus `GATE_EXCLUDED`, a named fnmatch list of SSOT and session-evidence files that lives only in `exec_checks.py`; the ps1 copy is removed and `plan_checks.py static` asserts the plan's list equals it. `post-review-state` re-runs the suites that read excluded files, now including `tests/tooling/test_framework_adoption.py`. | `GATED_PATHS`, `GATE_FINGERPRINT`; `exec_checks.py` `GATE_EXCLUDED`, `is_gated`; `plan_checks.py` `check_constants`; H2-2; D-29 |
| F7 (Low, clerical): OpenAPI template `{job_id}` | **Fixed.** `/api/v1/tts/{id}`, as `openapi.committed.json:6208` names the route, in the plan and in `exec_checks.OPENAPI_PATHS`, with a selftest case. | `OPENAPI_DIFF` |
| F8 (Low, clerical): `review-check` compared `target_plan` as a string | **Fixed.** `check_review` resolves `target_plan` as a path against this checkout (`same_file`); an absolute worktree target passes and another checkout's path fails, both as selftest cases. The report is still copied verbatim. | `exec_checks.py` `check_review`, `same_file` |

The plan's own record is `implementation-plan.md` §Round 1 Review Corrections and Decision Log D-25 to D-29.

### Census (PR-6)

`docs/execution/plans/2026-10-14-backend-robustness/review-r1-census.md` lists every replaced and introduced value, its hits and the disposition of each hit. Receipts: `C:/Temp/av-kit/census-backend-robustness-old.txt` and `C:/Temp/av-kit/census-backend-robustness-new.txt` (`rg -n -F` over the six plan-local files, `MSYS_NO_PATHCONV=1`). The first census pass caught a stale `D-8 to D-24` at `task.md:60`, fixed before the receipts were recorded.

### Verification results

Run 2026-10-15 from `P:/av-kit-wt/backend-robustness` at HEAD `78610200`; every command exited 0. Receipts are in `C:/Temp/av-kit/`.

| Receipt | Result |
|---|---|
| `s33-plan-static.txt` | `PASS static: 24 task rows` |
| `s33-plan-selftest.txt` | 19 of 19 injected defects reported |
| `s33-plan-exec-selftest.txt` | 65 of 65 cases |
| `s33-plan-lint.txt` | `OK: 24 row(s)` |
| `s33-plan-ps1parse.txt` | parsed, no errors |
| `s33-plan-pycompile.txt` | compiled, no errors |

Ready for round 2 of `/plan-critical-review`.

---

## Round 2 Review (2026-10-15)

> **Intent anchor:** "Session 33 delivers MEU-76 (logged, CORS-safe unhandled errors and a typed extract error), MEU-78 (one live ffmpeg resolver for Convert, TTS, health and yt-dlp) and MEU-77 (TTS generate returns the job at once, synthesizes in the background and can be cancelled), with an OpenAPI diff limited to those contracts and an MCP audit in which tts.cancel passes."

**Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial.
One High finding remains blocking. No Critical findings. Seven round-1 findings are closed at plan level.

## Scope

Independent round 2, loop s33-plan-2026-10-14-backend-robustness. Author/corrector: Claude Code, Anthropic. Reviewer: Codex gpt-6.1-sol, OpenAI; this reviewer authored neither the plan nor corrections.

All repository observations used P:/av-kit-wt/backend-robustness, branch claude/backend-robustness, HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba. Relative references below resolve there. P denotes docs/execution/plans/2026-10-14-backend-robustness. Reviewed P/implementation-plan.md, task.md, validate-task.ps1, exec_checks.py, plan_checks.py, baseline_carry.py and review-r1-census.md, the rolling round-1 report/correction section, REVIEW-TEMPLATE 2.2, vocabulary, residual specifications, grouping, issue SSOT and affected source/test callers.

Applied the nine workflow sweeps, PR-1–PR-9, DR-1–DR-8 and relevant adversarial checks. The corrected plan remains unstarted: all 24 task rows are unchecked; baseline.sha, walkthrough.md and the three implementation handoffs are absent. Git status reports only the untracked plan directory and rolling plan review; tracked diff is empty.

No repository files were written, and no plan/product/test files in P:/av-kit were read. Only the assigned report and scratch receipts were written, plus the permitted selftest's temporary fixtures. User receipt-only scope and final-JSON requirement override the workflow's canonical-write/timestamp suffix. No timestamp script or additional verifier verb was run. The completion-preflight skill was consulted for report completeness; its implementation checklist does not authorize executing these pending tasks.

## Findings

| # | Severity / Confidence | Blocking | Kind / Subject | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F2 | High / High | yes | behavior / deliverable | Shutdown admission is locked, but worker registration is still outside that critical section. generate publishes a Generating row and _current_id, releases _lock, then calls _spawn. stop_processing can run in that interval, set _closing and the cancel flag, and observe no running worker through wait_idle. It can return True and permit model/database teardown before the accepted worker starts. The timeout fix therefore leaves the worker-registration part of round-1 F2 open. Violates AC-77 (SHUTDOWN_STOP; AC-77.9; PR-8). | P/implementation-plan.md:131,136,301 | Define accepted-but-not-started work as busy until spawn failure or _finish completes, with its reservation published under the admission lock. Make stop/wait_idle drain that reservation as well as running work. Add a bounded barrier test pausing after admission and before thread registration, calling stop, and proving it cannot return True or permit teardown before that job finishes; cover spawn failure while stopping. | open |

**Vocabulary mapping:** F2 is behavior, with no mechanism field: this is an unsafe planned runtime lifecycle result, not a completion-predicate bypass, verdict transition, or review-conduct detector failure. The closed vocabulary was read. No control-defeat finding or invented mechanism is introduced this round.

### Decisive trace and materiality

1. ASYNC_GENERATE at implementation-plan.md:131 explicitly adds/commits the Generating row, sets _current_id and clears the flag under _lock, then calls _spawn afterward. The default spawn starts and retains a daemon thread for wait_idle.
2. Pause the generating caller immediately before that spawn. There is accepted work, but no thread has yet been registered or started.
3. SHUTDOWN_STOP at :136 can acquire the same lock, set _closing and the flag, release it and call wait_idle. The specified idle condition is "once no worker is running"; no reservation-to-worker synchronization or pending-spawn condition is named.
4. On that permitted True result the lifespan unloads the model and disposes the engine. Resume the generating caller: it starts the accepted worker after teardown. WORKER_RULE still enters prepare/synthesis and needs those dependencies; checking cancellation during progress does not undo the unsafe teardown.

This is a missing concurrency contract in the planned service, established by static interleaving analysis, not a claim that product code has already been implemented or a runtime failure was reproduced. It directly violates the corrected contract's no-teardown-under-owned-work purpose. A coder could choose a safe implementation, but the plan currently permits this unsafe one and none of AC-77.9(a)–(d) forces this interval. Round-1 F2 expressly requested synchronization with worker registration (prior report :38,50); retaining it is not escalation to a nearby new predicate mutation.

Do not simply hold the non-reentrant lock while invoking an arbitrary injected spawn: FIXTURE_REPAIRS permits a synchronous spawn whose worker must eventually acquire _lock in _finish. Publish a reservation or equivalent lifecycle state before release, and define when it is discharged.

## Recheck (2026-10-15)

### Prior Pass Summary / Closure Table

| Finding | Status | Current evidence and substantive conclusion |
|---|---|---|
| F1 | closed | implementation-plan.md:132–134,297; D-25 :610–619. _finish decides terminal state, writes it, cleans up as needed and clears ownership/flag under the same lock cancel uses. AC-77.5(a) covers cancellation from output hooks; (b) holds the terminal save inside the lock and proves a later cancel cannot leak into the next job. |
| F2 | open | implementation-plan.md:131,136,301. False now skips unload/dispose and _closing prevents later admission, but an already admitted job is not explicitly reserved against the pre-spawn idle observation. See the sole finding above. |
| F3 | closed | implementation-plan.md:139,305,630–639; existing plan.ts:231–274 and run.ts:313–327. Bounded retry is restricted to Done after ineffective confirmed cancellation, with all refusal checks preserved. Each newly POSTed id is separately ledger-registered. |
| F4 | closed | validate-task.ps1:304–335; exec_checks.py:519–548; implementation-plan.md:148. The audit measures before preparation and after carry/expectation, rejects inequality, and gate-check compares both with the current computed audit fingerprint. |
| F5 | closed | validate-task.ps1:300–331; baseline_carry.py:65–80; implementation-plan.md:151. Every attempt restores the baseline.sha blob before the runner and supplies that same pre-session copy to carry. Explicit error branches restore the start-of-check baseline and delete plan-folder audit evidence, including git-show nonzero at :325. |
| F6 | closed | exec_checks.py:48–56,284–309; plan_checks.py:158–166; validate-task.ps1:515–519. The specifically omitted inputs are now gated by the whole-tree complement, with one executable exclusion list. Post-review reruns include the adoption test that copies current-focus. Coverage remains subject to the declared exclusions and endpoint-hash limits described below. |
| F7 | closed | implementation-plan.md:140; exec_checks.py:81,845–855; openapi.committed.json:6208. The existing /api/v1/tts/{id} template is allowed, with a direct selftest case. |
| F8 | closed | exec_checks.py:332–352,910–929. Absolute and relative paths resolve against this checkout; another checkout is rejected; mode, round, reviewer and verdict checks remain. Goal containment remains in plan_checks.py:233–240 and the dispatch ledger contract, not in check_review itself. |

### Confirmed Fixes

The timeout branch, cancellation terminal serialization, audit race handling, repeatable baseline comparison, audit interval fingerprint, omitted-input coverage and target-path normalization are substantive changes. Passing static/selftests support their implemented tooling portions; they do not prove the future product behavior.

### Remaining Findings

F2, High, blocking, behavior: complete admission-to-worker registration synchronization before implementation readiness.

## Answers to R1–R5

### R1 — Closure

Seven findings close as shown above; F2 closes its timeout/teardown-result branch but remains open on the explicitly requested registration race. No other round-1 finding is regressed. TA-1 through TA-10 retain the round-1 review's exact source-backed approvals; no additional assertion amendment is authorized by this report.

### R2 — Concurrency and bounded tests

For a registered/running worker, CANCEL_RULE now gives the necessary ordering. If cancel wins the lock before _finish, the terminal step sees the flag and writes Cancelled after partial cleanup. If _finish wins, it commits and clears ownership before cancel can proceed, making that later cancel a no-op. Unlocked early checks cannot override the terminal step. Clearing the flag alongside _current_id prevents it reaching another admitted job. Unknown/completed ids do not set it.

AC-77.5(b) actually tests **the terminal writer winning the lock**, not a cancel winning between the final check and lock acquisition: its repository barrier is inside _finish's critical section, the helper remains blocked after join(0.2), then Done/output retention and the next job are checked. This is a useful deterministic serialization oracle. AC-77.5(a) supplies the complementary cancel-before-finish cases through write/convert hooks. BOUNDED_WAIT requires an asserted event-arrival wait before launching the helper and asserted bounded completion waits; the plan does not promise a scheduler delay alone establishes arrival. No new blocker is raised for additional variants of fixed F1.

WORKER_RULE specifies one outcome, a Failed default for exceptions before selection, and exactly one _finish in finally. ASYNC_GENERATE separately handles a throwing spawn through _finish and re-raises; ordinary spawn failure does not strand a row. _closing is checked before row creation in the same lock as the busy check, so a new admission after stop is rejected without a row. The unresolved case is admission **before** stop but spawn **after** its idle check (F2).

AC-77.9(b) uses a 0.2-second stop timeout, and (c) controls the stop result with spies: neither needs a real ten-second wait. All fake waits must still terminate within BOUNDED_WAIT and be released during cleanup. False skips both destructive teardown calls, logs api.shutdown_tts_busy and leaves recovery to the next startup if process exit interrupts the daemon. That is the specified safe fail-closed timeout policy; a successful late worker may instead finish normally before exit. The existing restart test covers the stale Generating row. These tests start after the port is entered or stub the result; they do not force F2's pending-spawn interval.

PARTIAL_CLEANUP deliberately logs and ignores unlink OSError. It guarantees attempted cleanup under ordinary writable-filesystem conditions, not physical deletion when the filesystem refuses. This pre-existing explicit limitation is not newly escalated. Repository/commit failure inside _finish is also outside the illustrated successful-collaborator concurrency proof; no product execution evidence is claimed.

### R3 — Audit and gate evidence

**Retry correctness.** AUDIT_CANCEL_STEP repeats the precondition/reestablish block and entire refusal sequence, at most three attempts. Refusal failure, confirmed error, Failed terminal or still-Generating after polling cannot be retried under the stated conjunction. A Done result alone cannot pass: an attempt must actually observe Cancelled. This allows bounded recovery from natural completion; it is not proof that every historical attempt cancelled successfully. AC-77.13 covers first success, Done-then-success, exhaustion and still-running failure; Failed/refusal failures are explicit production requirements even though those subcases are not separately enumerated there.

The existing cleanup ledger is a map keyed by kind:id (ledger.ts:11–26), not a single tts_job slot. Registering every replacement id retains all jobs across retries. run.ts:313–327 iterates them and DELETEs each /tts/id. Up to three additional ids does not exceed a ledger cap. Existing TTS cleanup means cancellation/isolated-run cleanup, not deletion of every completed output via a new REST endpoint; no such endpoint is required here.

**Fingerprints.** The before measurement now precedes uv sync/build; the after measurement follows carry and AUDIT_EXPECT. Persistent gated edits during the audit, between audit and Windows gate, or after the gate are refused on current-tree recomputation. The generated baseline is excluded only from the audit fingerprint and is included in the Windows gate fingerprint. The previously missing plan contract, baseline_carry, old plan/grouping, workflow/docs/schema/template inputs are now in scope.

This is endpoint comparison, not a continuous lease: transient edit-and-revert is not detected; a comparison establishes freshness when invoked. Final independent execution review must check current identity. Recorded external registry/framework identities and runtime versions are not remeasured by check_gate; this is the inherited round-1 evidence limit, not a newly corrected guarantee.

**Exclusions.** SSOT and renders, issues, grouping/focus, dated handoffs/reflection/metrics, audit report, task status, walkthrough and result receipts are closeout state. The status/BUILD_PLAN readers are covered by layout-canon/queue-canon; the adoption fixture copies current-focus indirectly through its manifest. post-review-state reruns those, gui-actions-audit, MCP docs and test_framework_adoption. MCP docs mostly reads now-gated workflows/skill/index files; its rerun is conservative. The search of tests, ui/tests and mcp-server/tests found no additional concrete reader of a Session-33 excluded file omitted by that rerun.

The exclusion list is intentionally broader than the strictly mutable subset: baseline.sha should remain immutable, all task.md bytes are excluded although only status/evidence should change, and *.json/*.txt patterns cover more than the currently named output files. Therefore "every gate input is bound" should be read with its declared exclusions and later checks, not as a literal assertion that no input is outside the digest. This round found no new materially missing Session-33 product deliverable false-passing solely through those exclusions. Per the materiality/nearby-mutation rules, this does not reopen fixed F6 or add a deeper predicate finding.

**Comparison and rollback.** Every runner invocation receives the pre-session blob at the baseline path; computeDelta:123–125 therefore sees fail→pass again as FIXED on a successful rerun. A nonzero git show, prep failure, runner failure, carry refusal, expectation failure or fingerprint refusal reaches AuditFail. Evidence is removed at entry before preparation, so failure cannot silently retain an earlier plan-folder success. git show fails before copying its output over the baseline.

The rollback is explicit-path handling, not a universal exception transaction: PowerShell terminating I/O/launch exceptions can bypass AuditFail, and process termination cannot be made transactional by these statements. Such paths fail the script and normally leave no complete pair of audit evidence files; do not describe them as a successful restored check. This is a residual operational limitation, not the prior reproducible FIXED/UNCHANGED dead end or a demonstrated new success bypass.

**F8/intent.** same_file does not weaken target containment to a basename match. Its absolute-other-checkout selftest fails. check_review never performs the ledger's intent/author-provenance validation; that remains the dispatch/ledger responsibility. plan_checks still checks the goal sentence in the review prompt. No claim that frontmatter alone authenticates approval is made here.

### R4 — Census adequacy / PR-6

Both raw receipts are present and untruncated. Independently reran each of their 37 literal searches against exactly the six named current files and compared every matching file:line:content record: **37 matches, zero mismatched searches**. Old searches yield zero hits except four $gated guard/selftest lines, all dispositioned and consistent. The correction log's grouped introduced-value dispositions cover the raw hits; the unchanged /tts/{id} references also agree with the actual committed route. No incorrect substantive per-hit disposition was found.

Six files are the right scope for the **edited planning artifacts**, but not the whole semantic blast radius. Additional siblings exist in TTS service/lifespan/wiring, the old synchronous tests/fakes, audit destructiveStep and tts_job cleanup, fixtures and delta classifier, committed OpenAPI, and tests that read excluded files. This review inspected/swept those separately. Their old synchronous implementation is expected in an unstarted plan; the Files Modified tables/TA and repair census schedule those changes. In particular, audit plan.ts's tts_job1 get step stays correct while only cancel moves to tts_job2; run.ts's multi-id ledger already supports retries. The plan-local review-prompt-plan.md also exists outside the six-file census; its round-1 wording is historical and the explicit current dispatch controls this round. It adds no competing live corrected product contract.

The census validates propagation of the written corrections. It cannot establish that D-26 actually resolves all F2 interleavings; that disposition is rejected by this substantive review. PR-6's evidence precondition passes; approval still fails on the runtime contract.

### R5 — Regressions / completion predicates

No new independent finding is introduced. F2 is retained with the same identity and delivery-level behavior classification. No new control-defeat mechanism is asserted. The newly implemented tooling changes close the specific round-1 defects; no concrete new materially missing deliverable was shown to pass a completion predicate. Static/selftests test their own cases, not runtime cancellation, real audit success or complete environment authentication.

## Checklist Results

Manual checks below used observer gpt-6.1-sol and exit_code null. Procedures are concrete file comparison, source call-chain tracing and interleaving analysis; they are not unobserved execution claims.

### Plan Review

| Check | Result | Procedure and decisive evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compared all 24 task rows and named contracts; order remains 76→78→77; H1 audit precedes Windows gate and final review. |
| PR-2 Not started | pass | Git status/log/diff and Test-Path; only plan/review untracked; baseline and implementation handoffs absent; task rows unchecked. |
| PR-3 Task contract | pass | Read task table and static result: 24 rows with owners, deliverables, dependencies and commands. |
| PR-4 Validation realism | partial | Three allowed verifiers pass; future runtime tests are scheduled, but AC-77.9 does not force the pending-spawn race. |
| PR-5 Source-backed planning | pass | Compared source-labelled FICs with residual 03/04, grouping and issue homes; no new external assertion needs web research. |
| PR-6 Census/handoff readiness | pass | Both raw receipts plus disposition log inspected; all 37 searches exactly match current files; semantic siblings checked outside the six files; handoff set explicit. |
| PR-7 Scope discipline | pass | Deferred MEU-72–75/79 exist in SSOT/grouping; no required residual feature is silently deferred. |
| PR-8 Reachability/atomicity/totality | fail | F2's accepted job reaches spawn outside the admission lock, permitting shutdown to observe no registered worker. Other corrected cancel/audit chains are explicit. |
| PR-9 Single statement | pass | Named definitions, executable-copy parity and literal census compared; no new materially conflicting duplicate contract found. |

### Documentation Review

| Check | Result | Procedure and decisive evidence |
|---|---|---|
| DR-1 Claim/state | partial | Unstarted status correct; correction summary's F2 fixed claim exceeds the synchronized contract. |
| DR-2 Old terms | pass | Reproduced raw old-value searches; four $gated hits are intentional guards/selftest. Product old terms remain scheduled implementation work. |
| DR-3 References | pass | Checked corrected route template, same-checkout target resolution and D-25–D-29 references. |
| DR-4 Robustness | partial | Negative verifier cases pass; terminal race/timeout designs improved; missing pending-spawn oracle remains F2. |
| DR-5 Auditability | pass | Commands, preserved exits and decisive output embedded below; no product-suite success inferred. |
| DR-6 Canon integrity | pass | Read residual Spec and reconciliation inventory for cached/synchronous/MCP cancel wording. |
| DR-7 Freshness | pass | Three allowed verifiers freshly run; census search outputs compared with current files. |
| DR-8 Completion/risk | pass | This report explicitly withholds readiness; no implementation-complete claim. |

### Template / Information Retrieval / Adversarial Checks

| Check | Result | Procedure and evidence |
|---|---|---|
| Source labels, exact validation and BUILD_PLAN audit | pass | Read FIC source columns, task validation cells and plan :360–388; all three MEU handoffs plus H2 reflection/metrics scheduled. |
| Naming, template and frontmatter | pass | Compared REVIEW-TEMPLATE 2.2 and the user's exact ten frontmatter keys; report uses round 2. |
| AV-1 failing-then-passing proof | partial | Red/Green design scheduled; no runtime results exist yet; F2 needs the specified additional barrier. |
| AV-2/AV-4 bypass/skip masking | pass | Reviewed Red/Green parsers and selftest cases; refusal failures cannot be retried under AUDIT_CANCEL_STEP. |
| AV-3 assertion coverage | partial | AC catalogue covers intended product surfaces; concurrency coverage gap is F2. |
| AV-5 completed placeholders / execution FAIL_TO_PASS bundle | n/a | Unstarted plan, not an implementation completion review. |
| AV-6 criteria basis | pass | Residual contracts and local lifecycle sources read; no unsourced new scope added. |

All nine required sweeps were performed: alignment; readiness; role fields; exact command/consumer tracing; dependency order; source labels; scope discipline; existence of runner/template/config/script dependencies; repeated-literal census. Twelve sampled invoked script/config/template paths exist (listed in the command evidence); static also checks every Files Modified create/modify target. New runtime test files are explicitly scheduled, so their current absence is expected.

## Commands Executed and Output

All shell cwd values were P:/av-kit-wt/backend-robustness. Tools were routed through rtk proxy. Process evidence was redirected under C:/Temp/av-kit, $LASTEXITCODE captured immediately and propagated after reading the completed receipt. Initial bounded bootstrap reads loaded the workflow, terminal-preflight and output policy. A memory-registry search for Session 33/backend-robustness found no hits and supplied no review facts.

### Static inspection commands

Executed git status --short, git log -1 --format="%H %s", git diff --stat and git branch --show-current, through RTK. Decisive output:

```text
?? .agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md
?? docs/execution/plans/2026-10-14-backend-robustness/
78610200ea2e7efd52318ea95c3e48b6df4993ba docs(closeout): Session 30 H2 — reflection, MEU-67 approved, issues resolved
claude/backend-robustness
git diff --stat: empty
```

Git status emitted permission warnings reading C:/Users/Mat/.config/git/ignore; exit 0. No content of that file was read or printed. All subsequent repository observations remained in the worktree.

Executed rtk proxy pwsh -NoProfile -Command with Get-Content (numbered slices for long files) for the protocol, guardrails/profile, prior report/corrections, template/vocabulary, all seven review targets, product source/canon/readers named in this report, reviewer/completion guidance and review-verdict schema. These completed with exit 0. Source excerpts decisive to F2 are quoted/traced above; they were observed at plan :131 and :136, not inferred from correction prose.

Additional executed searches (each exit 0) were:

```text
rtk proxy rg -n -e 'current-focus|meu-status|meu-registry|known-issues|BUILD_PLAN|metrics\.md|backend-robustness|baseline-counts|baseline\.sha|mcp-tool-audit-report|task\.md|handoffs|reflections' tests ui/tests mcp-server/tests
rtk proxy rg -n -e '_cancel_ids|_finish_done|stop_processing|wait_idle|generate is synchronous|tts_job1|tts_job2|raceLost|attempts' packages/core/src/avkit_core/services/tts.py packages/api/src/avkit_api/main.py packages/api/src/avkit_api/wiring.py mcp-server/scripts/audit/plan.ts mcp-server/scripts/audit/run.ts mcp-server/scripts/audit/fixtures.ts tests/unit/test_services.py tests/integration/test_tts_assets.py
rtk proxy rg -n -e 'MEU-7[2-9]|33 \||API-UNHANDLED-ERROR-OPAQUE|FFMPEG-RESOLUTION-DIVERGENCE|MCP-TTS-GENERATE-SYNCHRONOUS' .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md .agent/context/meu-status.yaml .agent/context/known-issues.yaml
rtk proxy rg -n -e 'Cleanup|register|outstanding|computeDelta|FIXED|UNCHANGED' mcp-server/scripts/audit/ledger.ts mcp-server/scripts/audit/classify.ts
rtk proxy rg -n -e 'wait_idle|stop_processing|_finish|CANCEL_RULE|AUDIT_|GATED_PATHS|job_id|target_plan|round|F[1-8]|raceLost|D-24|D-29|Generating' docs/execution/plans/2026-10-14-backend-robustness/review-prompt-plan.md
```

Decisive search outputs: layout-canon reads status/hub at :18–19; queue-canon reads the same at :18–19; old TTS ownership/cancel sites are :87,111,167,172,199,209,252; audit fixtures:20 still has the scheduled synchronous comment; plan.ts:648,664–665 use tts_job1 for completed generation/get while :676–677 is the scheduled cancel replacement; classify.ts:123 maps pass/pass to UNCHANGED and :125 nonpass/pass to FIXED; ledger.ts:15–16 registers by kind:id. Grouping Session 33 is pending at :188, order :107; the named residual/deferred MEUs are present in SSOT. The old review prompt contains round-1 instructions, treated as historical data.

Test-Path observations: baseline.sha, walkthrough.md and MEU-76/78/77 implementation handoffs all False. The following twelve invoked dependencies were True:

```text
tools/export_openapi.py
tools/meu_status.py
tools/issue_triage.py
tools/lint_task_contract.py
tools/validate_closeout_artifacts.py
tools/Invoke-CodexDispatch.ps1
ui/package.json
mcp-server/package.json
ui/playwright.config.ts
.agent/schemas/reflection.v1.yaml
docs/execution/reflections/TEMPLATE.md
.agent/context/handoffs/REVIEW-TEMPLATE.md
```

### Reproduced census

The census comparison command used a read-only PowerShell loop: extract each literal from each raw receipt's "=== rg -n -F" header, invoke rtk proxy rg -n -F -- PATTERN against the six explicit P/... file paths, preserve native exit, normalize only the common directory prefix, and Compare-Object every resulting file:line:content record against that receipt's records. Zero-hit rg exit 1 is a valid census result; any >1 or record mismatch would fail the comparison. Overall exit 0. Complete comparison output follows in the appended evidence section.

### Permitted verifier runs

Only these three Python verbs were executed, with RECEIPTS_DIR=C:/Temp/av-kit and PYTHONDONTWRITEBYTECODE=1. Each exited 0. Their complete captured output follows; expected FAIL entries are successful negative selftest cases, not failed commands.

## Open Questions and Residual Risk

No new human product decision is needed. The author can resolve F2 within the existing lifecycle intent. No tests, builds, installers, generators, validate-task checks or live MCP audit were run. Product behavior, real model timing, Electron behavior and network audit success remain unmeasured. Endpoint hashing, declared closeout exclusions, external-environment remeasurement and exception-interrupted rollback retain the stated limits; they are not additional blockers this round.

## Verdict

**changes_required** — intent achieved **partial** at plan level. The error surface, shared live resolver, cancellation terminal ordering and corrected audit tooling are coherently planned, but the remaining F2 admission-to-spawn interval can allow shutdown teardown under accepted background work.

## Follow-Up Actions

1. Through /plan-corrections, define and test a pending-spawn reservation/idle predicate, including spawn failure while stopping, without deadlocking the supported synchronous test spawn.
2. Update only affected contract/AC/caller descriptions and the blast-radius census; rerun the three plan-local verifiers.
3. Continue the same plan loop for ledger round 3, respecting its registered cap. Preserve this report and the round-1 record.
4. Dispatcher appends this report verbatim to the canonical rolling review. This reviewer does not edit the plan, implement fixes or chain into execution.

Report: C:/Temp/av-kit/dispatch/s33-plan-review-report.md

Canonical destination (dispatcher-owned): P:/av-kit-wt/backend-robustness/.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md

## Captured Verifier and Census Output


### plan_checks.py static (exit 0)

~~~text
$ rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static
PASS static: 24 task rows; script, exec_checks, plan contracts, references and file targets agree
~~~


~~~json
{"schema_version":"evidence.v1","check_id":"s33-r2-static","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static","cwd":"P:/av-kit-wt/backend-robustness","scope":"Session 33 planning verifiers only","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba; unstarted corrected Session 33 plan","output":"PASS static: 24 task rows; script, exec_checks, plan contracts, references and file targets agree","fresh":true}
~~~


### plan_checks.py selftest (exit 0)

~~~text
$ rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py selftest
PASS selftest duplicate row id: duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6',
PASS selftest unknown check: task.md invokes -Check 'no-such-check', which validate-task.ps1 does not define
PASS selftest swapped stage: stage order differs: ps1=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-bui
PASS selftest gate exclusion added: GATED_PATHS differ: plan GATE_EXCLUDED=['.agent/context/meu-status.yaml', '.agent/context/meu-registry.md', '.agent/context/current-focus.md
PASS selftest ps1 gated copy: GATED_PATHS differ: validate-task.ps1 holds its own $gated copy
PASS selftest changed floor: COUNT_FLOORS differ: plan={'pytest': 600, 'vitest': 773, 'e2e': 133} exec_checks={'pytest': 655, 'vitest': 773, 'e2e': 133}
PASS selftest AC tier changed: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'
PASS selftest AC row dropped: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'
PASS selftest pin dropped: pins differ: plan=set() exec_checks={'77.14'}
PASS selftest TA file changed: TEST_AMENDMENTS differ: plan={1: 'tests/unit/test_domain.py', 2: 'tests/integration/test_filesystem_media.py', 3: 'tests/unit/test_domain.py
PASS selftest source audit file dropped: $SRC76 differs from product_files: ps1-only={'x.ts'} plan-only={'ui/src/renderer/src/lib/api.ts'}
PASS selftest red without guard: red78 does not start with the red-guard
PASS selftest TA in red: red77 runs a TEST_AMENDMENTS array (TAs apply only in Green)
PASS selftest undefined AC: task.md references AC-78.99, which has no definition site
PASS selftest undefined D: task.md references D-99, which has no definition site
PASS selftest undefined TA: task.md references TA-11, which has no definition site
PASS selftest missing modify target: Files Modified 'modify' row names a missing file: ui/no/such/file.ts
PASS selftest existing create target: Files Modified 'create' row names a file that already exists: pyproject.toml
PASS selftest missing goal anchor: review-prompt-plan.md does not contain the Goal sentence (INTENT_BINDING)
PASS selftest: every injected defect was reported
~~~


~~~json
{"schema_version":"evidence.v1","check_id":"s33-r2-plan-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py selftest","cwd":"P:/av-kit-wt/backend-robustness","scope":"Session 33 planning verifiers only","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba; unstarted corrected Session 33 plan","output":"PASS selftest: every injected defect was reported","fresh":true}
~~~


### exec_checks.py selftest (exit 0)

~~~text
$ rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py selftest
  ok  pytest red76 good: PASS (expected PASS)
  ok  pytest red76 with a NEG_MARK pass: PASS (expected PASS)
  ok  pytest red76 TypeError (non-assertion): FAIL (expected FAIL) - non-assertion failure: tests.unit.test_x::test_ac_76_7_x: TypeError: unexpected keyword 's
  ok  pytest red76 missing AC-76.7: FAIL (expected FAIL) - AC-76.7 has no decisive assertion failure in pytest
  ok  pytest red76 tagged pass without NEG_MARK: FAIL (expected FAIL) - tagged test passed in Red (no NEG_MARK): tests.unit.test_x::test_ac_76_1_extra
  ok  pytest red76 untagged failure: FAIL (expected FAIL) - untagged test did not pass (failed): tests.unit.test_x::test_old_breaks
  ok  pytest red76 collection error: FAIL (expected FAIL) - collection error ::tests.unit.test_x: ImportError: x
  ok  pytest red76 ac_76_10 is not AC-76.1: FAIL (expected FAIL) - tests.unit.test_x::test_ac_76_10_x: AC-76.10 is not an AC of MEU-76
  ok  pytest red76 exit 0: FAIL (expected FAIL) - Red run exited 0
  ok  pytest red76 DID NOT RAISE counts: PASS (expected PASS)
  ok  vitest red76 good: PASS (expected PASS)
  ok  vitest red76 load error: FAIL (expected FAIL) - load error x.test.ts: Failed to resolve import
  ok  vitest red76 TypeError: FAIL (expected FAIL) - non-assertion failure: api AC-76.8 x: TypeError: Cannot read properties of undefined
  ok  vitest red76 AC-76.80 not AC-76.8: FAIL (expected FAIL) - AC-76.80 x: AC-76.80 is not an AC of MEU-76
  ok  mcp red76 jest-dom style expect: PASS (expected PASS)
  ok  electron red78 good: PASS (expected PASS)
  ok  electron red78 test timeout: FAIL (expected FAIL) - non-assertion failure: f.ts > AC-78.9 x: Test timeout of 30000ms exceeded.
  ok  electron red78 top-level error: FAIL (expected FAIL) - top-level error: Error: launch failed
  ok  electron red77 pin passes: PASS (expected PASS)
  ok  electron red77 pin fails: FAIL (expected FAIL) - pin test must pass in Red (failed): f.ts > AC-77.14 x
  ok  electron red77 pin flaky: FAIL (expected FAIL) - pin test must pass in Red (flaky): f.ts > AC-77.14 x
  ok  pytest green77 needs every AC: FAIL (expected FAIL) - AC-77.10 has no passing test in pytest
  ok  pytest green77 good: PASS (expected PASS)
  ok  pytest green77 a failure: FAIL (expected FAIL) - exit 1
  ok  fingerprint lines sorted, content-bound, deletions recorded
  ok  GATED_PATHS ui/src/x.ts: gated
  ok  GATED_PATHS .agent/workflows/mcp-audit.md: gated
  ok  GATED_PATHS .agent/docs/commands.md: gated
  ok  GATED_PATHS docs/execution/plans/TASK-TEMPLATE.md: gated
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md: gated
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/baseline_carry.py: gated
  ok  GATED_PATHS .agent/skills/mcp-tool-audit/resources/baseline-snapshot.json: gated
  ok  GATED_PATHS .agent/context/meu-status.yaml: excluded
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/windows-gate-result.json: excluded
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/task.md: excluded
  ok  GATED_PATHS .agent/context/handoffs/2026-10-14-backend-robustness-MEU-77-handoff.md: excluded
  ok  GATED_PATHS .agent/context/handoffs/2026-09-26-framework-update-adoption-implementation-critical-review.md: gated
  ok  audit fp good: PASS
  ok  audit fp moved during the audit: FAIL
  ok  audit fp tree changed after: FAIL
  ok  audit fp missing before: FAIL
  ok  openapi allowed change: PASS
  ok  openapi added path: FAIL
  ok  openapi other schema: FAIL
  ok  openapi other path: FAIL
  ok  openapi job route by its committed template {id}: PASS
  ok  audit good: PASS
  ok  audit cancel not FIXED: FAIL
  ok  audit regression: FAIL
  ok  audit cleanup failed: FAIL
  ok  audit baseline misses an action: FAIL
  ok  audit baseline commit drift: FAIL
  ok  gate good: PASS
  ok  gate tree changed after: FAIL
  ok  gate stage order: FAIL
  ok  gate e2e flaky: FAIL
  ok  gate pytest under carried floor: FAIL
  ok  gate mcp under row-0 floor: FAIL
  ok  gate fingerprint moved in run: FAIL
  ok  review good: PASS
  ok  review absolute worktree target: PASS
  ok  review other checkout target: FAIL
  ok  review self-authored agent: FAIL
  ok  review changes_required: FAIL
  ok  review over cap: FAIL
PASS selftest
~~~


~~~json
{"schema_version":"evidence.v1","check_id":"s33-r2-exec-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py selftest","cwd":"P:/av-kit-wt/backend-robustness","scope":"Session 33 planning verifiers only","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba; unstarted corrected Session 33 plan","output":"PASS selftest","fresh":true}
~~~


### Census comparison (exit 0)

~~~text
MATCH old {job_id} hits=0 rg_exit=1
MATCH old $gated hits=4 rg_exit=0
MATCH old audit-fingerprint.txt hits=0 rg_exit=1
MATCH old wait_idle(10.0) hits=0 rg_exit=1
MATCH old D-8 to D-24 hits=0 rg_exit=1
MATCH old Re-run the doc-reading suites hits=0 rg_exit=1
MATCH old GATED_PATHS = [ hits=0 rg_exit=1
MATCH old changed_paths(baseline_sha(), GATED_PATHS) hits=0 rg_exit=1
MATCH old ec.GATED_PATHS hits=0 rg_exit=1
MATCH old 'docs/proposals',  hits=0 rg_exit=1
MATCH old _finish_done hits=0 rg_exit=1
MATCH old Its `finally` clears `_current_id` hits=0 rg_exit=1
MATCH old gains a `precondition` that POSTs hits=0 rg_exit=1
MATCH old stop_processing()` sets the cancel flag hits=0 rg_exit=1
MATCH new /api/v1/tts/{id} hits=8 rg_exit=0
MATCH new GATE_EXCLUDED hits=17 rg_exit=0
MATCH new AUDIT_COMPARISON hits=8 rg_exit=0
MATCH new audit-fingerprint.json hits=8 rg_exit=0
MATCH new audit-fp hits=7 rg_exit=0
MATCH new raceLost hits=5 rg_exit=0
MATCH new attempts hits=5 rg_exit=0
MATCH new _closing hits=4 rg_exit=0
MATCH new _finish hits=6 rg_exit=0
MATCH new stop_timeout hits=2 rg_exit=0
MATCH new shutdown_tts_busy hits=2 rg_exit=0
MATCH new s33-baseline-presession hits=2 rg_exit=0
MATCH new s33-baseline-prior hits=2 rg_exit=0
MATCH new test_framework_adoption hits=4 rg_exit=0
MATCH new D-8 to D-29 hits=2 rg_exit=0
MATCH new D-25 hits=5 rg_exit=0
MATCH new D-26 hits=5 rg_exit=0
MATCH new D-27 hits=4 rg_exit=0
MATCH new D-28 hits=3 rg_exit=0
MATCH new D-29 hits=7 rg_exit=0
MATCH new same_file hits=3 rg_exit=0
MATCH new stop_processing hits=8 rg_exit=0
CENSUS mismatched searches=0
~~~


~~~json
{"schema_version":"evidence.v1","check_id":"s33-r2-concurrency-review","procedure":"Compare ASYNC_GENERATE and SHUTDOWN_STOP; enumerate stop between locked admission and unlocked spawn; compare AC-77.9 and the round-1 F2 registration requirement.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/backend-robustness","scope":"MEU-77 lifecycle contract","phase":"planning","exit_code":null,"result":"fail","tested_state":"unstarted corrected plan at HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba","output":"F2 remains open: accepted Generating row/current id precede worker spawn, but stop/wait_idle does not reserve accepted-not-started work against teardown.","fresh":true}
~~~

---

## Corrections Applied (2026-10-15, round 2)

> **Author:** Claude Code (plan author, coder role, running /plan-corrections). This section does not change the round 2 verdict above. The `changes_required` verdict, its finding and its R1–R5 answers stand as the reviewer wrote them. Plan-corrections Step 6 changes the frontmatter `verdict:` to `corrections_applied` to show the plan is ready for re-review. Only an independent `/plan-critical-review` round may set `approved`.

### Findings and dispositions

| Finding | Disposition | Where |
|---|---|---|
| F2 (High, behavior): shutdown could see idle between admission and worker registration | **Fixed (D-30).** `_current_id` is now the job's reservation. It is published inside the admission critical section, before `_lock` is released, and only `_finish` clears it, whether from the worker's `finally` or a spawn failure. `wait_idle` is `with self._idle: return self._idle.wait_for(lambda: self._current_id is None, timeout)`, with `_idle = threading.Condition(self._lock)`, and `_finish` calls `notify_all()` in its critical section. So an admitted job that has not been spawned, or whose thread has not started, counts as busy, and `stop_processing` cannot return `True` before its terminal write. Spawn stays outside the lock, because the synchronous spawn of `FIXTURE_REPAIRS` (a) runs a worker whose `_finish` takes `_lock`. The worker's first action reads the cancel flag; when a stop or cancel came before the thread started, the outcome is `Cancelled` and no port, filesystem or media method is called. `_finish` is the worker's last call into any collaborator. AC-77.9 (e) uses a deferred spawn: stop returns `False` while the job is reserved and unspawned, then the worker ends `Cancelled` without calling `prepare` or `generate`, and a second stop returns `True`. AC-77.9 (f) uses a spawn that blocks and then raises while a stop is waiting: the stop is still running after `join(0.2)` and returns `True` only after the spawn failure's `_finish`, with the row `Cancelled` and `_current_id` `None`. | `ASYNC_GENERATE`, `WORKER_RULE`, `CANCEL_RULE`, `SHUTDOWN_STOP`; AC-77.9 (e)-(f); D-30; `implementation-plan.md` §Round 2 Review Corrections |

### Census (PR-6)

`docs/execution/plans/2026-10-14-backend-robustness/review-r2-census.md` lists each replaced or re-meant value, its hits and the disposition of each. Because `wait_idle` changes meaning, the census also swept the product and test trees for `wait_idle` and `_current_id`. Receipts: `C:/Temp/av-kit/census-backend-robustness-r2-before.txt` (before the edit) and `C:/Temp/av-kit/census-backend-robustness-r2-after.txt` (after it).

**Receipt regeneration (2026-10-15, after the refused round 3 attempt).** The first version of both receipts was clipped at 200 to 220 characters by a display `cut`. A round 3 attempt rejected them under PR-6; the ledger refused that verdict over its `Violates:` citation, so no round was consumed and it is not part of this thread. Both receipts are regenerated untruncated. The before receipt runs over the pre-edit plan text, rebuilt by inverting the edit's one-shot replacements, and the rebuilt lines 103, 131-133, 136 and 301 each appear verbatim in the round 2 reviewer's event log. `review-r2-census.md` is rewritten to disposition every hit, including the hits the clipped version left out (`D-26`, the round 1 `AC-77.9` row, `test_tts_assets.py:639`).

### Verification results

Re-run 2026-10-15 from `P:/av-kit-wt/backend-robustness` after the edit. Every command exited 0. Receipts are in `C:/Temp/av-kit/`.

| Receipt | Result |
|---|---|
| `s33-plan-static.txt` | `PASS static: 24 task rows` |
| `s33-plan-selftest.txt` | 19 of 19 injected defects reported |
| `s33-plan-exec-selftest.txt` | 65 of 65 cases |
| `s33-plan-lint.txt` | `OK: 24 row(s)` |
| `s33-plan-ps1parse.txt` | parsed, no errors |
| `s33-plan-pycompile.txt` | compiled, no errors |

No script changed in this round; the correction is plan text only.

Ready for round 3 of `/plan-critical-review`.

---

## Round 3 Review (2026-10-15)

> **Intent anchor:** "Session 33 delivers MEU-76 (logged, CORS-safe unhandled errors and a typed extract error), MEU-78 (one live ffmpeg resolver for Convert, TTS, health and yt-dlp) and MEU-77 (TTS generate returns the job at once, synthesizes in the background and can be cancelled), with an OpenAPI diff limited to those contracts and an MCP audit in which tts.cancel passes."

**Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial.
One High blocking finding; no Critical findings. PR-6 passes. The previously refused attempt is not counted as a ledger round or adopted as this report's verdict.

## Scope

Independent review, loop `s33-plan-2026-10-14-backend-robustness`, final permitted round 3. Author/corrector: Claude Code, Anthropic. Reviewer: Codex `gpt-6.1-sol`, OpenAI, class `avkit_independent_reviewer`; the reviewer authored neither plan nor corrections.

Every repository command ran in `P:/av-kit-wt/backend-robustness`, branch `claude/backend-robustness`, HEAD `78610200ea2e7efd52318ea95c3e48b6df4993ba`. In this report, **P** abbreviates `docs/execution/plans/2026-10-14-backend-robustness/`; all relative file references resolve in that worktree.

Reviewed P/implementation-plan.md, task.md, validate-task.ps1, exec_checks.py, plan_checks.py, baseline_carry.py and review-r2-census.md; the rolling review/corrections; both regenerated census receipts; the residual specification, relevant production callers and existing test fixtures. Applied the nine plan-review sweeps, PR-1–PR-9, DR-1–DR-8 and relevant reviewer adversarial checks. REVIEW-TEMPLATE 2.2 and the previous round supply structure and the comparison baseline.

The plan is unstarted: all 24 task rows are unchecked, tracked diff is empty, and baseline.sha, walkthrough.md and the three implementation handoffs are absent. The only untracked entries are this session's plan directory and rolling plan review.

No repository file was written. No plan, product or test file in `P:/av-kit` was read. Writes were confined to this report and review receipts under `C:/Temp/av-kit`, plus the explicitly permitted evaluator selftest's system temporary fixtures. No product tests, builds, generators, validate-task checks or MCP audit ran. The user's receipt-only/final-JSON instructions supersede generic workflow instructions to write the canonical review or execute a timestamp script. The dispatcher owns appending this report verbatim.

## Findings

| # | Severity / Confidence | Blocking | Kind / Subject | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F2 | High / High | yes | behavior / deliverable | D-30 drains the worker reservation but not the admitted generate caller. ASYNC_GENERATE still calls self.get_status(job.id) after _spawn; a fast worker can finish and clear _current_id before that database read. stop_processing can then return True and authorize database disposal while the admitted caller can still enter its UnitOfWork. Violates: AC-77. | docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md:131-133,136; packages/core/src/avkit_core/services/tts.py:103-108 | Cover the admitted caller's final database access in the drain contract, or eliminate that post-reservation collaborator access while preserving synchronous-spawn terminal results. Add a bounded barrier case with worker completion before the generating caller's response read; prove stop cannot authorize teardown while that read remains possible. | open |

**Classification mapping:** F2 remains `behavior`, subject `deliverable`; no mechanism is assigned. It is an unsafe runtime lifecycle result, not task-row-completion-predicate, verdict-to-state-transition or review-conduct-detection. The closed vocabulary was read; no new control-defeat slug is invented. No other new finding is raised, and no closed finding is reopened.

### Decisive trace and materiality

The original accepted-but-unspawned worker interleaving is now closed. However, the drain's ownership interval still ends before the last collaborator access of the admitted operation:

1. `ASYNC_GENERATE` (plan :131) commits the row and publishes `_current_id` under `_lock`, then releases it and spawns the worker.
2. Pause the **generating caller** after `_spawn` and before its specified `return self.get_status(job.id)`. This is possible with the default thread spawn; no adversarial spawn implementation is needed.
3. The worker completes `_finish`: it commits its terminal result and clears `_current_id` under `_lock` (plan :133). `WORKER_RULE` makes this the worker's final collaborator access (:132).
4. Concurrent `stop_processing` sets `_closing`; `Condition.wait_for(lambda: self._current_id is None, timeout)` is immediately true (:131,136). The lifespan is consequently allowed to unload/dispose (:136,328).
5. Resume the generating caller. Its mandated `get_status` enters `_uow_factory()` and reads `tts_jobs.get` (current service :103-108), **after the drain has authorized database teardown**.

The same tail exists with the explicitly supported synchronous spawn: completing `fn()` releases the worker reservation before the calling `generate` does its return read. The instruction that `_finish` is the **worker's** last collaborator call does not cover this caller.

This is static interleaving evidence, not a runtime reproduction or a claim that a particular SQLAlchemy disposal must always make the next read fail. The concrete failed control is the planned lifecycle's affirmative permission to dispose while its own admitted operation still has database work. No caller-drain precondition is stated for `stop_processing`; request draining by a particular host is not the specified service synchronization mechanism. The existing pending-spawn and spawn-failure cases do not test this completed-worker/pending-caller state.

F2 is retained on the same resource-ownership requirement, with new file-level evidence identifying the outstanding caller tail. It is not a deeper mutation of a fixed completion predicate. Its requested correction can preserve the Condition and unlocked spawn; for example, account separately for admitted callers until their final read finishes, or return a safely captured job snapshot without a later database call. Do not hold the non-reentrant admission lock across synchronous spawn.

## Recheck (2026-10-15)

### Prior Pass Summary / Closure Table

| Finding | Status | Evidence and conclusion |
|---|---|---|
| F1 | closed | Plan :132-134,297: cancel and terminal selection/write share `_lock`; `_finish` clears flag/ownership atomically. D-30 adds notification without changing that ordering. Cancel-before-finish output hooks and finish-before-cancel barrier remain specified. |
| F2 | open | Plan :131-133,136,301,665-669: pre-spawn reservation, notification and timeout handling close the worker-registration branch. The caller still performs `get_status` after that reservation can clear; service :103-108 proves this is a database collaborator access. |
| F3 | closed | Plan :139,305,693: three bounded audit attempts; retries require held refusals, ineffective successful confirmation and terminal Done. Actual Cancelled remains the pass oracle; Failed/still-Generating/refusal failures cannot be converted into success. Ledger :15-26 retains every replacement id. |
| F4 | closed | validate-task.ps1 :304-335 fingerprints before preparation and after carry/expectation; exec_checks.py :519-548 requires before == after == current. No D-30 change weakens that chain. |
| F5 | closed | validate-task.ps1 :300-331 restores the baseline.sha blob on every attempt and gives the same pre-session copy to carry. Failure branches restore the start-of-check baseline and remove attempt evidence. classify.ts :123-125 still computes fail-to-pass as FIXED. |
| F6 | closed | exec_checks.py :284-309 uses the whole-tree complement; plan :146 names exclusions. Runner :515-519 reruns the excluded-file readers, including framework adoption. Previous endpoint-fingerprint/exclusion limits remain acknowledged, not a new missing-deliverable false-pass. |
| F7 | closed | Plan :140 and exec_checks.py OPENAPI_PATHS (:81) use `/api/v1/tts/{id}`; current route :95,101 agrees. The permitted selftest explicitly accepts that route. |
| F8 | closed | exec_checks.py :332-352 resolves the target against this checkout; current selftest passes the absolute worktree target and rejects another checkout. Mode, reviewer, round and verdict checks remain. |

### Confirmed Fixes

D-30 correctly publishes worker ownership before admission unlock, treats deferred/unstarted work as busy, and uses one lock for the Condition predicate and notification. It keeps synchronous spawn outside the lock and adds a pre-work cancellation path. Those are substantive fixes to the round-2 worker-registration defect. They do not extend the reservation through the caller's return read.

### Remaining Findings

F2 only: High, blocking, behavior. Seven other findings remain closed. TA-1–TA-10 retain their previously approved exact scope; this review authorizes no additional assertion amendments.

## Answers to R1–R4

### R1 — Does the drain prevent every admitted job from reaching a collaborator after True?

**For the worker: yes. For the complete admitted generate operation: no.** Plan :131 publishes the reservation in the admission critical section; :133 clears/notifies only after the terminal write; :132 prohibits worker collaborator calls afterward. Therefore stop cannot successfully drain an unspawned or active worker. But :131's generating caller still calls `get_status` after `_spawn`, outside that lifetime. The trace above is the remaining F2 evidence. False still skips both unload and disposal (:136), so the timeout fix remains sound.

### R2 — Condition, cancellation, synchronous spawn and test interleavings

No Condition deadlock or lost notification is introduced by the stated algorithm: `wait_for` tests `_current_id` while holding the same lock used by `_finish`; waiting releases that lock; notification occurs while `_finish` owns it. Finishing before the waiter arrives is safe because the waiter checks the predicate before waiting. `_finish`'s UoW/cleanup must complete before ownership clears.

`stop_processing` releases `_lock` before entering `wait_idle`; `cancel` takes it only to change the current job's flag. Spawn remains outside the lock. Thus `FIXTURE_REPAIRS` (a)'s synchronous worker can take it in `_finish`. The real test callback at `tests/unit/test_services.py:1748-1751` calls cancel during the port invocation, which is also outside that critical section. No recursive lock acquisition is required by that path.

The new idle meaning preserves AC-77.1, TA-7–TA-10 and repair (f): a successful service wait observes the terminal write because reservation release follows it. `Stack.wait_idle` at `test_tts_assets.py:155-161` instead polls model-download runtime and returns a dictionary; its 13 call sites are unrelated. TA-9's overlap comment at :639 remains consistent once the preceding worker is awaited.

AC-77.9(e) forces pending work: spawn stores the callable without running it, then the first stop must time out; running that callable must produce Cancelled without prepare/generate; the second stop must succeed. This catches the former thread-only idle implementation independently of scheduling luck.

AC-77.9(f) describes A stopped inside spawn and B not returning until spawn-failure `_finish` discharges the reservation. All waits/joins remain bounded by :144. **Implementation caution:** arrange an asserted arrival signal for A and an observable stop/closing signal for B before releasing A; `join(0.2)` alone proves noncompletion, not that B has entered stop. Otherwise a slow scheduler can release A before the cancel flag is set and make a correct implementation produce Failed. This is a test-implementation requirement for the stated interleaving, not a second blocking finding. Neither (e) nor (f) exercises F2's completed-worker/pending-response-read interval.

### R3 — Census adequacy / PR-6

**Pass.** Both regenerated receipts contain complete matching lines rather than 200–220-character fragments. Independently repeated all **18** after-receipt literal searches against its six files and compared full `file:line:content` records: **zero mismatched searches**. Zero-hit old values remain zero-hit. Dispositions cover each record, including historical D-26 and the round-1 AC-77.9 row now at :692. `_idle` substring matches are correctly covered by the wait_idle dispositions.

The before receipt explicitly discloses reconstruction rather than claiming a contemporaneous capture. Its distinct pre-edit records at plan :103,131,133,136,301 were independently found verbatim in decoded strings from the round-2 event log. Those are the pre-edit records actually inventoried by that receipt. The reviewer corrected an initial string-representation comparison to use decoded event strings; this was an inspection issue, not missing provenance.

An independent current product/test search over packages, tests, ui and mcp-server returned the same **20** raw hits as the before receipt's product/test sections: 14 model-runtime wait_idle hits, four service _current_id hits, the unit cancellation callback and the TA-9 comment at test_tts_assets.py:639. Every semantic sibling has a disposition in review-r2-census.md :33-48. In particular, the callback and model-runtime method were checked in their real bodies. This census proves propagation of the correction; it does not prove the complete lifecycle safe, and does not cover the unnamed caller-tail access found by the substantive review.

### R4 — Previously closed findings

F1 and F3–F8 remain closed for the evidence in the table. No new evidence makes their previous closure unsound. The OpenAPI allow-list and audit contracts still match the registered goal; actual product success remains future execution work.

## Checklist Results

Manual procedures in the following tables were performed by **gpt-6.1-sol**, with **exit_code null**. They are static comparisons/traces, not product execution claims.

### Plan Review

| Check | Result | Observed procedure and decisive evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compared all 24 task rows with named contracts: order 76 → 78 → 77; H1 audit/full gate before review, H2 afterward. |
| PR-2 Not started | pass | Git status/log/diff plus artifact-existence reads: unchecked tasks; no baseline, walkthrough or implementation handoffs. |
| PR-3 Task contract | pass | Read task :34-62 and static output: 24 rows with owners, deliverables, dependencies and exact commands. |
| PR-4 Validation realism | partial | Three allowed verifiers pass; runtime cases are explicit, but AC-77.9 omits the caller-tail oracle in F2. |
| PR-5 Source-backed planning | pass | Compared FIC source columns with residual Spec 03:468-494, current main/service/wiring and named local canon. |
| PR-6 Census/corrections readiness | pass | Raw receipts, 18 exact search comparisons, prior-event provenance, 20 product/test hits and per-hit log dispositions checked. Three handoff paths are explicit. |
| PR-7 Scope discipline | pass | Read out-of-scope :348-358; deferred MEU-72–75/79 exist in SSOT at :1909-2088. Shutdown remains included rather than deferred. |
| PR-8 Reachability/atomicity/totality | fail | Reservation/Condition/cancel chain is explicit, but generate → post-spawn get_status → UoW remains reachable after successful drain (F2). |
| PR-9 Single-statement discipline | pass | Named definitions, census and static executable-copy checks agree. No materially conflicting duplicate state set found. |

### Documentation Review

| Check | Result | Observed procedure and decisive evidence |
|---|---|---|
| DR-1 Claim/state match | partial | Unstarted status is accurate; F2 fixed claim does not account for the final caller read. |
| DR-2 Residual old terms | pass | Old after-census searches reproduced; remaining D-26 and old correction-row references are historical and dispositioned. |
| DR-3 Downstream references | pass | D-30 and H2 decision range agree; correct route and absolute review target remain recognized. |
| DR-4 Verification robustness | partial | Selftests reject their injected defects; added runtime designs cover the worker interval, not F2's caller tail. |
| DR-5 Evidence auditability | pass | Preserved exits and decisive observations below; complete outputs of all permitted verifiers embedded. |
| DR-6 Cross-reference integrity | pass | Residual contracts, reconciliation inventory and current service/lifespan callers compared. |
| DR-7 Evidence freshness | pass | Verifiers and after-census independently observed against this worktree during round 3. Reconstructed before evidence is labelled as such. |
| DR-8 Completion versus risk | pass | Draft implementation remains pending; this review withholds readiness and claims no product completion. |

### Information Retrieval / Template / Adversarial Checks

| Check | Result | Procedure and evidence |
|---|---|---|
| Source labels; exact validation; BUILD_PLAN audit; post-MEU rows | pass | Read FICs, plan :360-388 and all task rows; three handoffs, reflection and metrics are scheduled. |
| Naming, template version and frontmatter | pass | Compared REVIEW-TEMPLATE 2.2 and the user's exact ten requested frontmatter keys. |
| Referenced artifacts exist | pass | Twelve sampled script/config/template dependencies all exist; static checks Files Modified targets. Missing new tests are explicitly scheduled creates. |
| AV-1 / AV-3 Red/Green design and assertion coverage | partial | Named ACs and negative oracles exist, but F2 needs the additional lifecycle barrier. Product failing/passing results are not yet available. |
| AV-2 / AV-4 bypass and skip masking | pass | Reviewed evaluator/selftest negative cases and unchanged refusal rules; no new skip/bypass is prescribed. |
| AV-6 source-backed criteria | pass | Read residual contracts and local lifecycle sources; no new feature scope requested. |
| Completed execution bundle / FAIL_TO_PASS / AV-5 completed placeholders | n/a | This is an unstarted plan, not an implementation-completion review. |

All nine sweeps were performed: alignment, readiness, task fields, validation specificity, dependency order, source traceability, scope discipline, referenced-artifact existence and repeated-literal census. Their observations appear above; no prohibited execution was substituted for static inspection.

## Commands Executed and Output

Shell cwd was always `P:/av-kit-wt/backend-robustness`. Commands used `rtk proxy`, receipts under `C:/Temp/av-kit`, and immediate `$LASTEXITCODE` preservation before receipt reads. File reads used `rtk proxy python -X utf8 -c` with `Path.read_text`, numbered bounded ranges for long files; these were inspection helpers, not additional project-verifier verbs. Census comparisons used completed rg receipts and PowerShell `Compare-Object`. No repository module was imported by those read helpers.

### Static observations

| Actual command / procedure | Exit | Decisive output |
|---|---|---|
| `rtk proxy git status --short --branch` | 0 | `## claude/backend-robustness`; only `?? .agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md` and `?? docs/execution/plans/2026-10-14-backend-robustness/`. Two permission warnings for the global git-ignore path; no contents read. |
| `rtk proxy git log -1 --format='%H %s'` | 0 | `78610200ea2e7efd52318ea95c3e48b6df4993ba docs(closeout): Session 30 H2 — reflection, MEU-67 approved, issues resolved` |
| `rtk proxy git diff --stat` | 0 | Empty output. |
| `rtk proxy rg -n -F -- <literal> <six plan files>` for every after-receipt section | 0 comparison; rg 0/1 as expected | `AFTER census mismatches=0 sections=18`. Full line records matched, including zero-hit searches. |
| `rtk proxy rg -n -F -e wait_idle -e _current_id packages tests ui mcp-server` | 0 | 20 matches: integration model-runtime method/callers, the cancel callback, TA-9 comment and service ownership sites; all dispositioned. |
| Decoded gzip/JSON read of round-2 events, comparing exact before-receipt source lines | 0 | `plan:131 EXACT_TEXT_PRESENT`; `plan:136 EXACT_TEXT_PRESENT`; `plan:103 EXACT_TEXT_PRESENT`; `plan:301 EXACT_TEXT_PRESENT`; `plan:133 EXACT_TEXT_PRESENT`. |
| `rtk proxy rg -n -A 4 -e 'id: MEU-7[2-9]' .agent/context/meu-status.yaml` | 0 | MEU-72–79 present at :1909,1935,1959,1985,2010,2034,2062,2088. |
| `rtk proxy rg -n -e 'dont_write_bytecode|def |selftest|ROOT|__main__|TemporaryDirectory|GATE_EXCLUDED|OPENAPI_PATHS' P/plan_checks.py P/exec_checks.py P/baseline_carry.py` (P expanded) | 0 | Static/evaluator entrypoints, bytecode suppression, selftest tempfile and closure consumers located; relevant definitions read. |
| Numbered file reads of protocol, AGENTS, GUARDRAILS, PROFILE, rolling review, template, vocabulary, schema, harness/focus/issues, reviewer/completion guidance and artifact naming | 0 | Protocol, v2.2 template, closed vocabulary and v2 verdict requirements loaded; only the dispatched review scope applied. |
| Numbered target/source reads described in scope and closure tables | 0 | Plan :131 still returns `self.get_status(job.id)`; current service :104 opens the UoW. Plan :133 clears the only wait predicate before that caller read. |
| Artifact existence read | 0 | Twelve dependencies True: export_openapi.py, meu_status.py, issue_triage.py, lint_task_contract.py, validate_closeout_artifacts.py, Invoke-CodexDispatch.ps1, UI/MCP package.json, Playwright config, reflection schema/template and REVIEW-TEMPLATE. Baseline, walkthrough and three implementation handoffs False. |

Incidental reviewer inspection errors: the initial nested-shell bootstrap had a ParserError; its replacement first encountered a console UnicodeEncodeError and then succeeded with UTF-8. Two later read-expression syntax errors were corrected before consuming their output. One resource search included nonexistent `tests/e2e/test_api_shell.py` and exited 2; its partial output was not used as a complete census. An unrelated memory-registry keyword search returned only other-project history and supplied no review facts. These are not plan findings or product test failures.

Final readback used `rtk proxy rg -n` on this report's frontmatter, headings, F1–F8 rows, verifier PASS lines and cap statement (exit 0): round 3, findings_count 1, changes_required, all required sections and all three complete verifier outputs were present. Final `rtk proxy git status --short --branch` also exited 0 with exactly the initial worktree entries and the same global-ignore warnings.

### Permitted verifier commands — complete fresh output

The following three commands each exited **0**. Diagnostic truncation inside individual selftest messages is produced by the verifier itself, not by a clipped census. Expected FAIL diagnostics are successful negative cases.

~~~text
$ rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static
PASS static: 24 task rows; script, exec_checks, plan contracts, references and file targets agree
~~~

~~~text
$ rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py selftest
PASS selftest duplicate row id: duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6',
PASS selftest unknown check: task.md invokes -Check 'no-such-check', which validate-task.ps1 does not define
PASS selftest swapped stage: stage order differs: ps1=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-bui
PASS selftest gate exclusion added: GATED_PATHS differ: plan GATE_EXCLUDED=['.agent/context/meu-status.yaml', '.agent/context/meu-registry.md', '.agent/context/current-focus.md
PASS selftest ps1 gated copy: GATED_PATHS differ: validate-task.ps1 holds its own $gated copy
PASS selftest changed floor: COUNT_FLOORS differ: plan={'pytest': 600, 'vitest': 773, 'e2e': 133} exec_checks={'pytest': 655, 'vitest': 773, 'e2e': 133}
PASS selftest AC tier changed: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'
PASS selftest AC row dropped: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'
PASS selftest pin dropped: pins differ: plan=set() exec_checks={'77.14'}
PASS selftest TA file changed: TEST_AMENDMENTS differ: plan={1: 'tests/unit/test_domain.py', 2: 'tests/integration/test_filesystem_media.py', 3: 'tests/unit/test_domain.py
PASS selftest source audit file dropped: $SRC76 differs from product_files: ps1-only={'x.ts'} plan-only={'ui/src/renderer/src/lib/api.ts'}
PASS selftest red without guard: red78 does not start with the red-guard
PASS selftest TA in red: red77 runs a TEST_AMENDMENTS array (TAs apply only in Green)
PASS selftest undefined AC: task.md references AC-78.99, which has no definition site
PASS selftest undefined D: task.md references D-99, which has no definition site
PASS selftest undefined TA: task.md references TA-11, which has no definition site
PASS selftest missing modify target: Files Modified 'modify' row names a missing file: ui/no/such/file.ts
PASS selftest existing create target: Files Modified 'create' row names a file that already exists: pyproject.toml
PASS selftest missing goal anchor: review-prompt-plan.md does not contain the Goal sentence (INTENT_BINDING)
PASS selftest: every injected defect was reported
~~~

~~~text
$ rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py selftest
  ok  pytest red76 good: PASS (expected PASS)
  ok  pytest red76 with a NEG_MARK pass: PASS (expected PASS)
  ok  pytest red76 TypeError (non-assertion): FAIL (expected FAIL) - non-assertion failure: tests.unit.test_x::test_ac_76_7_x: TypeError: unexpected keyword 's
  ok  pytest red76 missing AC-76.7: FAIL (expected FAIL) - AC-76.7 has no decisive assertion failure in pytest
  ok  pytest red76 tagged pass without NEG_MARK: FAIL (expected FAIL) - tagged test passed in Red (no NEG_MARK): tests.unit.test_x::test_ac_76_1_extra
  ok  pytest red76 untagged failure: FAIL (expected FAIL) - untagged test did not pass (failed): tests.unit.test_x::test_old_breaks
  ok  pytest red76 collection error: FAIL (expected FAIL) - collection error ::tests.unit.test_x: ImportError: x
  ok  pytest red76 ac_76_10 is not AC-76.1: FAIL (expected FAIL) - tests.unit.test_x::test_ac_76_10_x: AC-76.10 is not an AC of MEU-76
  ok  pytest red76 exit 0: FAIL (expected FAIL) - Red run exited 0
  ok  pytest red76 DID NOT RAISE counts: PASS (expected PASS)
  ok  vitest red76 good: PASS (expected PASS)
  ok  vitest red76 load error: FAIL (expected FAIL) - load error x.test.ts: Failed to resolve import
  ok  vitest red76 TypeError: FAIL (expected FAIL) - non-assertion failure: api AC-76.8 x: TypeError: Cannot read properties of undefined
  ok  vitest red76 AC-76.80 not AC-76.8: FAIL (expected FAIL) - AC-76.80 x: AC-76.80 is not an AC of MEU-76
  ok  mcp red76 jest-dom style expect: PASS (expected PASS)
  ok  electron red78 good: PASS (expected PASS)
  ok  electron red78 test timeout: FAIL (expected FAIL) - non-assertion failure: f.ts > AC-78.9 x: Test timeout of 30000ms exceeded.
  ok  electron red78 top-level error: FAIL (expected FAIL) - top-level error: Error: launch failed
  ok  electron red77 pin passes: PASS (expected PASS)
  ok  electron red77 pin fails: FAIL (expected FAIL) - pin test must pass in Red (failed): f.ts > AC-77.14 x
  ok  electron red77 pin flaky: FAIL (expected FAIL) - pin test must pass in Red (flaky): f.ts > AC-77.14 x
  ok  pytest green77 needs every AC: FAIL (expected FAIL) - AC-77.10 has no passing test in pytest
  ok  pytest green77 good: PASS (expected PASS)
  ok  pytest green77 a failure: FAIL (expected FAIL) - exit 1
  ok  fingerprint lines sorted, content-bound, deletions recorded
  ok  GATED_PATHS ui/src/x.ts: gated
  ok  GATED_PATHS .agent/workflows/mcp-audit.md: gated
  ok  GATED_PATHS .agent/docs/commands.md: gated
  ok  GATED_PATHS docs/execution/plans/TASK-TEMPLATE.md: gated
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md: gated
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/baseline_carry.py: gated
  ok  GATED_PATHS .agent/skills/mcp-tool-audit/resources/baseline-snapshot.json: gated
  ok  GATED_PATHS .agent/context/meu-status.yaml: excluded
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/windows-gate-result.json: excluded
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/task.md: excluded
  ok  GATED_PATHS .agent/context/handoffs/2026-10-14-backend-robustness-MEU-77-handoff.md: excluded
  ok  GATED_PATHS .agent/context/handoffs/2026-09-26-framework-update-adoption-implementation-critical-review.md: gated
  ok  audit fp good: PASS
  ok  audit fp moved during the audit: FAIL
  ok  audit fp tree changed after: FAIL
  ok  audit fp missing before: FAIL
  ok  openapi allowed change: PASS
  ok  openapi added path: FAIL
  ok  openapi other schema: FAIL
  ok  openapi other path: FAIL
  ok  openapi job route by its committed template {id}: PASS
  ok  audit good: PASS
  ok  audit cancel not FIXED: FAIL
  ok  audit regression: FAIL
  ok  audit cleanup failed: FAIL
  ok  audit baseline misses an action: FAIL
  ok  audit baseline commit drift: FAIL
  ok  gate good: PASS
  ok  gate tree changed after: FAIL
  ok  gate stage order: FAIL
  ok  gate e2e flaky: FAIL
  ok  gate pytest under carried floor: FAIL
  ok  gate mcp under row-0 floor: FAIL
  ok  gate fingerprint moved in run: FAIL
  ok  review good: PASS
  ok  review absolute worktree target: PASS
  ok  review other checkout target: FAIL
  ok  review self-authored agent: FAIL
  ok  review changes_required: FAIL
  ok  review over cap: FAIL
PASS selftest
~~~

~~~json
{"schema_version": "evidence.v1", "check_id": "s33-r3-plan-selftest", "command": "rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py selftest", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "permitted plan-local negative cases", "phase": "planning", "exit_code": 0, "result": "pass", "tested_state": "unstarted round-2-corrected Session 33 plan at HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba", "output": "PASS selftest duplicate row id: duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6',\nPASS selftest unknown check: task.md invokes -Check 'no-such-check', which validate-task.ps1 does not define\nPASS selftest swapped stage: stage order differs: ps1=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-bui\nPASS selftest gate exclusion added: GATED_PATHS differ: plan GATE_EXCLUDED=['.agent/context/meu-status.yaml', '.agent/context/meu-registry.md', '.agent/context/current-focus.md\nPASS selftest ps1 gated copy: GATED_PATHS differ: validate-task.ps1 holds its own $gated copy\nPASS selftest changed floor: COUNT_FLOORS differ: plan={'pytest': 600, 'vitest': 773, 'e2e': 133} exec_checks={'pytest': 655, 'vitest': 773, 'e2e': 133}\nPASS selftest AC tier changed: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'\nPASS selftest AC row dropped: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'\nPASS selftest pin dropped: pins differ: plan=set() exec_checks={'77.14'}\nPASS selftest TA file changed: TEST_AMENDMENTS differ: plan={1: 'tests/unit/test_domain.py', 2: 'tests/integration/test_filesystem_media.py', 3: 'tests/unit/test_domain.py\nPASS selftest source audit file dropped: $SRC76 differs from product_files: ps1-only={'x.ts'} plan-only={'ui/src/renderer/src/lib/api.ts'}\nPASS selftest red without guard: red78 does not start with the red-guard\nPASS selftest TA in red: red77 runs a TEST_AMENDMENTS array (TAs apply only in Green)\nPASS selftest undefined AC: task.md references AC-78.99, which has no definition site\nPASS selftest undefined D: task.md references D-99, which has no definition site\nPASS selftest undefined TA: task.md references TA-11, which has no definition site\nPASS selftest missing modify target: Files Modified 'modify' row names a missing file: ui/no/such/file.ts\nPASS selftest existing create target: Files Modified 'create' row names a file that already exists: pyproject.toml\nPASS selftest missing goal anchor: review-prompt-plan.md does not contain the Goal sentence (INTENT_BINDING)\nPASS selftest: every injected defect was reported", "fresh": true}
{"schema_version": "evidence.v1", "check_id": "s33-r3-exec-selftest", "command": "rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py selftest", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "permitted plan-local negative cases", "phase": "planning", "exit_code": 0, "result": "pass", "tested_state": "unstarted round-2-corrected Session 33 plan at HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba", "output": "ok  pytest red76 good: PASS (expected PASS)\n  ok  pytest red76 with a NEG_MARK pass: PASS (expected PASS)\n  ok  pytest red76 TypeError (non-assertion): FAIL (expected FAIL) - non-assertion failure: tests.unit.test_x::test_ac_76_7_x: TypeError: unexpected keyword 's\n  ok  pytest red76 missing AC-76.7: FAIL (expected FAIL) - AC-76.7 has no decisive assertion failure in pytest\n  ok  pytest red76 tagged pass without NEG_MARK: FAIL (expected FAIL) - tagged test passed in Red (no NEG_MARK): tests.unit.test_x::test_ac_76_1_extra\n  ok  pytest red76 untagged failure: FAIL (expected FAIL) - untagged test did not pass (failed): tests.unit.test_x::test_old_breaks\n  ok  pytest red76 collection error: FAIL (expected FAIL) - collection error ::tests.unit.test_x: ImportError: x\n  ok  pytest red76 ac_76_10 is not AC-76.1: FAIL (expected FAIL) - tests.unit.test_x::test_ac_76_10_x: AC-76.10 is not an AC of MEU-76\n  ok  pytest red76 exit 0: FAIL (expected FAIL) - Red run exited 0\n  ok  pytest red76 DID NOT RAISE counts: PASS (expected PASS)\n  ok  vitest red76 good: PASS (expected PASS)\n  ok  vitest red76 load error: FAIL (expected FAIL) - load error x.test.ts: Failed to resolve import\n  ok  vitest red76 TypeError: FAIL (expected FAIL) - non-assertion failure: api AC-76.8 x: TypeError: Cannot read properties of undefined\n  ok  vitest red76 AC-76.80 not AC-76.8: FAIL (expected FAIL) - AC-76.80 x: AC-76.80 is not an AC of MEU-76\n  ok  mcp red76 jest-dom style expect: PASS (expected PASS)\n  ok  electron red78 good: PASS (expected PASS)\n  ok  electron red78 test timeout: FAIL (expected FAIL) - non-assertion failure: f.ts > AC-78.9 x: Test timeout of 30000ms exceeded.\n  ok  electron red78 top-level error: FAIL (expected FAIL) - top-level error: Error: launch failed\n  ok  electron red77 pin passes: PASS (expected PASS)\n  ok  electron red77 pin fails: FAIL (expected FAIL) - pin test must pass in Red (failed): f.ts > AC-77.14 x\n  ok  electron red77 pin flaky: FAIL (expected FAIL) - pin test must pass in Red (flaky): f.ts > AC-77.14 x\n  ok  pytest green77 needs every AC: FAIL (expected FAIL) - AC-77.10 has no passing test in pytest\n  ok  pytest green77 good: PASS (expected PASS)\n  ok  pytest green77 a failure: FAIL (expected FAIL) - exit 1\n  ok  fingerprint lines sorted, content-bound, deletions recorded\n  ok  GATED_PATHS ui/src/x.ts: gated\n  ok  GATED_PATHS .agent/workflows/mcp-audit.md: gated\n  ok  GATED_PATHS .agent/docs/commands.md: gated\n  ok  GATED_PATHS docs/execution/plans/TASK-TEMPLATE.md: gated\n  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md: gated\n  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/baseline_carry.py: gated\n  ok  GATED_PATHS .agent/skills/mcp-tool-audit/resources/baseline-snapshot.json: gated\n  ok  GATED_PATHS .agent/context/meu-status.yaml: excluded\n  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/windows-gate-result.json: excluded\n  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/task.md: excluded\n  ok  GATED_PATHS .agent/context/handoffs/2026-10-14-backend-robustness-MEU-77-handoff.md: excluded\n  ok  GATED_PATHS .agent/context/handoffs/2026-09-26-framework-update-adoption-implementation-critical-review.md: gated\n  ok  audit fp good: PASS\n  ok  audit fp moved during the audit: FAIL\n  ok  audit fp tree changed after: FAIL\n  ok  audit fp missing before: FAIL\n  ok  openapi allowed change: PASS\n  ok  openapi added path: FAIL\n  ok  openapi other schema: FAIL\n  ok  openapi other path: FAIL\n  ok  openapi job route by its committed template {id}: PASS\n  ok  audit good: PASS\n  ok  audit cancel not FIXED: FAIL\n  ok  audit regression: FAIL\n  ok  audit cleanup failed: FAIL\n  ok  audit baseline misses an action: FAIL\n  ok  audit baseline commit drift: FAIL\n  ok  gate good: PASS\n  ok  gate tree changed after: FAIL\n  ok  gate stage order: FAIL\n  ok  gate e2e flaky: FAIL\n  ok  gate pytest under carried floor: FAIL\n  ok  gate mcp under row-0 floor: FAIL\n  ok  gate fingerprint moved in run: FAIL\n  ok  review good: PASS\n  ok  review absolute worktree target: PASS\n  ok  review other checkout target: FAIL\n  ok  review self-authored agent: FAIL\n  ok  review changes_required: FAIL\n  ok  review over cap: FAIL\nPASS selftest", "fresh": true}
~~~

### Durable evidence

```json
{"schema_version":"evidence.v1","check_id":"s33-r3-static","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static","cwd":"P:/av-kit-wt/backend-robustness","scope":"plan-local static consistency","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba; unstarted round-2-corrected Session 33 plan; tracked diff empty","output":"PASS static: 24 task rows; script, exec_checks, plan contracts, references and file targets agree","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-r3-pr6","procedure":"Repeat all 18 after-receipt literal searches and compare complete records; check before source records against decoded round-2 events; compare current 20 product/test hits and disposition log.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/backend-robustness","scope":"round-2 correction census","phase":"planning","exit_code":null,"result":"pass","tested_state":"round-3 reviewed worktree","output":"18 searches, zero mismatches; five inventoried pre-edit source lines present verbatim in round-2 event strings; all 20 product/test hits covered.","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-r3-f2","procedure":"Trace admission, worker _finish, successful Condition drain and generate caller's post-spawn get_status into UnitOfWork; enumerate the paused-caller interleaving.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/backend-robustness","scope":"MEU-77 shutdown lifecycle","phase":"planning","exit_code":null,"result":"fail","tested_state":"unstarted corrected plan at HEAD 78610200ea2e7efd52318ea95c3e48b6df4993ba","output":"Worker ownership clears before the admitted generate caller's final database read; stop can return True and authorize disposal before that read. F2 remains open.","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-r3-product-execution","procedure":"Honor the static-only review restriction; run no product suites, builds, generators, validate-task checks or live audit.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/backend-robustness","scope":"product execution","phase":"planning","exit_code":null,"result":"not_run","tested_state":"unstarted plan","output":"The three permitted plan-local verifier passes establish tooling checks only; no runtime product success claimed."}
```

## Open Questions / Assumptions / Residual Risk

No human answer was needed to identify the static lifecycle gap. Collaborator I/O failure, refused unlink cleanup, fingerprint endpoint/declared-exclusion limits and actual audit/runtime timing remain the previously stated execution risks; none is escalated into a new finding here. The report does not assert that database disposal always causes a deterministic request failure. It does establish that the promised shutdown ownership boundary omits a reachable database access by an admitted operation.

The completion-preflight skill was consulted for canonical task state and review-artifact completeness. All 24 implementation rows remain deliberately pending. Its execution-persistence instructions do not authorize this reviewer to implement or mutate the plan.

## Verdict

**changes_required** — PR-6 passes and D-30 closes the unspawned-worker gap, but F2 remains open because successful drain can precede the admitted generating caller's final database access. **Intent achieved: partial** at plan level. F1 and F3–F8 remain closed; no Critical finding and no additional new finding.

## Follow-Up Actions

1. Dispatcher appends this complete report verbatim to the canonical rolling review and records the matching v2 verdict in the same loop.
2. Preserve F2 and the exact trace. The correction must either drain the admitted caller as well as the worker or avoid its post-reservation collaborator access; its bounded negative oracle must force the completed-worker/pending-caller interval.
3. **Round 3 exhausts the plan-review cap. Stop for Mat's direction under S7; do not automatically correct and dispatch a fourth round, reset the loop or start implementation.** This reviewer makes no repository edits and chains into no other workflow.

Report: `C:/Temp/av-kit/dispatch/s33-plan-review-report.md`.

Canonical destination (dispatcher-owned): `P:/av-kit-wt/backend-robustness/.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md`.

---

## Corrections Applied (2026-10-15, round 3)

> **Author:** Claude Code (plan author, coder role, running /plan-corrections). This section does not change the round 3 verdict above. The `changes_required` verdict, its finding and its R1–R4 answers stand as the reviewer wrote them. Plan-corrections Step 6 changes the frontmatter `verdict:` to `corrections_applied` to show the plan is ready for re-review. Only an independent `/plan-critical-review` round may set `approved`.

### Direction under S7

Round 3 used the last permitted round and asked for Mat's direction. Mat chose in chat on 2026-10-15 to fix F2 and run a fourth round. The ledger records it: `review_ledger.py continue --by Mat` at 2026-10-15T09:48:16-04:00, adding 1 round and 10,000,000 tokens (rounds 3/4, tokens 29,330,785/40,000,000; receipt `C:/Temp/av-kit/s33-plan-ledger-continue.txt`). The loop was not reset and the reviewer was not changed.

### Findings and dispositions

| Finding | Disposition | Where |
|---|---|---|
| F2 (High, behavior): D-30 drains the worker reservation but not the admitted generate caller | **Fixed (D-31).** Every `generate` call now counts as busy from entry to return. At entry, under `_lock`, it raises `ConflictError` when `_closing` is set, before any collaborator call, and otherwise increments `_callers`. Everything after entry runs inside a `try` whose `finally` takes `_idle`, decrements `_callers` and calls `notify_all()`. So the count falls only after the call's last collaborator access: the `get_status` read on success, or the spawn failure's `_finish`. `wait_idle` waits until `_current_id is None and _callers == 0`, so `stop_processing` cannot return `True`, and the lifespan cannot unload or dispose, while a caller can still open a unit of work. This also covers the model-port calls in the synchronous checks before admission (`get_model_status`, `list_voices`, `_require_assets`; `services/tts.py:131-139`). The admission check for `_closing` stays, for a stop that begins between entry and admission. `_lock` is never held across `spawn`, and the stored-row return (D-24) is kept for a synchronous spawn. AC-77.9 (g): a spawn fake runs the worker to `Done` and then blocks. While `_current_id` is already `None`, a `stop_processing(timeout=5.0)` on another thread is still running after `join(0.2)`. After release, the caller returns the `Done` row, the stop returns `True`, and a unit-of-work spy shows the last open coming before the stop's return. AC-77.9 (h): `list_voices` blocks before admission. A concurrent stop waits for it; the caller then raises `ConflictError` with no row added, and a later `generate` makes no `get_model_status` call. | `ASYNC_GENERATE`, `WORKER_RULE`, `SHUTDOWN_STOP`; AC-77.9 (g)-(h); D-31; `implementation-plan.md` §Round 3 Review Corrections |

### Census (PR-6)

`docs/execution/plans/2026-10-14-backend-robustness/review-r3-census.md` lists each replaced, extended or re-meant value, its hits and the disposition of each. It also covers the product and test hits for `get_status` and the `generate` callers, and the new entry-time refusal. Receipts, raw `rg` output with no `cut` or filter: `C:/Temp/av-kit/census-backend-robustness-r3-before.txt` (before the edit, over the live files; pre-edit copies in `C:/Temp/av-kit/s33-plan-pre-r3-snapshot/`) and `C:/Temp/av-kit/census-backend-robustness-r3-after.txt` (after it).

### Verification results

Re-run 2026-10-15 from `P:/av-kit-wt/backend-robustness` after the edit. Every command exited 0. Receipts are in `C:/Temp/av-kit/`.

| Receipt | Result |
|---|---|
| `s33-plan-static.txt` | `PASS static: 24 task rows` |
| `s33-plan-selftest.txt` | 19 of 19 injected defects reported |
| `s33-plan-exec-selftest.txt` | 65 of 65 cases |
| `s33-plan-lint.txt` | `OK: 24 row(s)` |
| `s33-plan-ps1parse.txt` | parsed, no errors |
| `s33-plan-pycompile.txt` | compiled, no errors |

No script changed in this round; the correction is plan text only.

Ready for round 4 of `/plan-critical-review`.

---

## Round 4 Review (2026-10-15)

> **Intent anchor:** "Session 33 delivers MEU-76 (logged, CORS-safe unhandled errors and a typed extract error), MEU-78 (one live ffmpeg resolver for Convert, TTS, health and yt-dlp) and MEU-77 (TTS generate returns the job at once, synthesizes in the background and can be cancelled), with an OpenAPI diff limited to those contracts and an MCP audit in which tts.cancel passes."

**Review Mode:** plan. **Verdict:** approved. **Intent achieved:** yes, at plan level.
No open blocking finding and no Critical finding. F2 is closed; F1 and F3–F8 remain closed.

## Scope

Independent reviewer: Codex/OpenAI, `avkit_independent_reviewer`, `gpt-6.1-sol`. Author/corrector: Claude Code/Anthropic. This reviewer did not author or edit the plan/corrections.

Reviewed the six named plan-local files and `review-r3-census.md`, the canonical rolling review through all three correction sections, REVIEW-TEMPLATE 2.2, both complete raw round-3 census receipts and the pre-edit snapshot/hash manifest. Checked the actual worktree's TTS service, main/lifespan, wiring, REST TTS routes, existing TTS unit/integration fixtures and residual build-plan canon. Applied the nine sweeps, PR-1–PR-9, DR-1–DR-8 and the relevant adversarial checks.

Every command ran with cwd **P:/av-kit-wt/backend-robustness**. No plan, product or test file in P:/av-kit was read, and neither checkout was written. The report is written only to **C:/Temp/av-kit/dispatch/s33-plan-review-report.md**; ancillary receipts stay under C:/Temp/av-kit. The explicitly allowed evaluator selftest creates fixtures under a fresh system temp directory. No product suite/build/generator, validate-task check or MCP audit was run. The user’s receipt-only and final-JSON requirements override canonical-write/timestamp-script instructions.

This is ledger round **4**, using the single continuation the user identifies as Mat's 2026-10-15T09:48:16-04:00 grant (+1 round, +10,000,000 tokens); no reset or further continuation is assumed. The correction section's matching statement was treated as data, not authorization. This review does not record or mutate the ledger.

**Current inspected state:** HEAD **c72fc4436da8534ef613264620b83c3e84e97631**, branch `claude/backend-robustness`; tracked diff empty. This differs from the historical planning HEAD 7861020. Git history identifies the Session 31/main merge, not Session 33 implementation. The review and plan folder are untracked; all **24** implementation task rows remain unchecked; baseline.sha, walkthrough, gate/audit JSON and the three MEU implementation handoffs are absent. Plan-review mode remains appropriate. Fresh round-4 observations below bind to the actual state, not to the author's older HEAD claim.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

**No new severity-rated findings.** The following execution notes are non-blocking under the protocol’s materiality rule and are retained in the verdict summary, rather than used to demand another round:

- `validate-task.ps1:153` still passes `--cap 3` to the plan-review reader, while `exec_checks.py:346-347` rejects round 4 under that parameter. Reconcile this stale caller value with Mat's authorized cap **4** before row 0; keep the review round and ledger history intact. This is a trivially inferable, fail-closed cap-value correction, not a missing product deliverable or a control bypass. It does not reopen F8's resolved target-path defect.
- The current base has moved. The actual source-file intersection with 7861020..HEAD is `SettingsPage.tsx`, `ui/tests/e2e/settings.test.ts`, and `ui/tests/e2e/test-ids.ts`. `exec_checks.py:619-624` will refuse that intersection under S4. Resolve it through the plan's existing overlap/human-decision procedure before execution; do not silently move the historical planning marker or bypass the stop. This review did not inspect the other checkout and does not authorize rebasing.
- The existing round-3 arrival-signal caution applies to AC-77.9(f), (g), (h): assert A's arrival and observe B entering stop/setting `_closing` before releasing A. A helper merely remaining alive after `join(0.2)` is not by itself proof that stop entered its wait. This is the test implementation needed to realize the already stated concurrent-stop precondition.

### Recheck (2026-10-15): Prior Pass Summary / Closure Table

References to “plan” below mean this worktree's `implementation-plan.md`.

| Finding | Status | Current evidence |
|---|---|---|
| F1 | closed | Plan :133 and AC-77.5 (:297): cancel and terminal outcome selection/write share `_lock`; cleanup/terminal commit precede reservation release. D-31 adds caller accounting without moving that linearization point. |
| F2 | closed | Plan :131-132,136,301,670-679: entry refuses a closing service before collaborators; otherwise caller count is retained through all checks, unlocked spawn and final stored-row read, then decremented/notified in finally. Idle requires both no reservation and zero callers. False still prevents unload/dispose. AC-77.9(g)/(h) cover completed-worker/pending-caller and pre-admission caller intervals. |
| F3 | closed | Plan :139,305: bounded three-attempt running-job audit, fresh target registration, retry only after held refusals + successful ineffective confirmation + terminal Done; actual Cancelled is the pass oracle. Failed/still-Generating/refusal failures remain failures. No D-31 change. |
| F4 | closed | Runner :304-335 measures audit fingerprint before prep and after carry/expectation; evaluator :519-548 requires before == after == current. All four scripts' hashes match the pre-round-3 snapshot. |
| F5 | closed | Runner :300-331 restores the pre-session baseline blob for every audit attempt and supplies it to carry; failure restores the start-of-check baseline and deletes this attempt's plan evidence. `check_audit` :379-380 still requires FIXED. No D-31 change. |
| F6 | closed | Evaluator :284-309 uses whole-tree complement membership; plan :146 explicitly names exclusions; runner :515-519 reruns excluded-file readers. Scope/fingerprint copy parity and negative cases still pass. Prior endpoint/exclusion limitations are not reopened. |
| F7 | closed | Plan :140 and evaluator :81 use `/api/v1/tts/{id}`; real routes :95,101 agree. Current selftest accepts that template and rejects unauthorized paths/schemas. |
| F8 | closed | Evaluator :332-352 resolves the absolute/relative target inside this checkout and checks mode, round, verdict and reviewer. Current selftest accepts the absolute target and refuses another checkout. The distinct stale cap caller is noted above without undoing this closure. |

**Classification mapping:** historical F1/F2/F3/F5 are behavior (no mechanism); historical F4/F6 are control-defeat mapped to **task-row-completion-predicate**, because those findings concerned acceptance of stale task-completion evidence; historical F7/F8 are clerical (no mechanism). They are closure rows, not new findings. The closed vocabulary was read: task-row-completion-predicate, verdict-to-state-transition, review-conduct-detection. No new control-defeat finding or invented slug is emitted.

## Answers to R1–R4

### R1 — Can successful stop/teardown precede a generate collaborator access?

**No, under the corrected plan's stated algorithm.** The decisive contract is plan :131, with teardown conditional on its result at :136.

1. Entry and stop serialize under the same `_lock`. If stop wins, entry raises before `get_model_status`, `list_voices`, assets/settings/UoW or any other collaborator. If entry wins, `_callers` increments before the first such access.
2. Before admission, that count remains nonzero while model/voice/assets checks run. A stop during them cannot drain successfully. The admission `_closing` recheck prevents adding a row after shutdown starts.
3. At admission, `_current_id` is published under `_lock`, before unlock. Between admission and spawn, inside a blocked/deferred spawn, or before a default thread starts, the reservation remains busy; the caller is also counted.
4. A worker may outlive the generating caller, so the reservation persists until its last collaborator operation in `_finish` (:132-133). Conversely, a worker may finish before its caller: even with `_current_id is None`, the caller count remains nonzero through the post-spawn `get_status` UoW. The return expression is evaluated before the caller's finally decrements/notifies.
5. Spawn failure's `_finish` and all synchronous failure paths stay inside the caller try/finally. The decrement cannot precede their final collaborator access.
6. `wait_idle` checks **both** components under `Condition(self._lock)`; successful stop therefore proves no worker or entered generate caller can still reach those collaborators. After stop sets closing, no new one can enter. A timeout returns False and lifespan skips both unload and disposal (:136).

The actual existing `get_status` opens a UoW at `services/tts.py:103-108`; model/voice/assets calls before admission are at :131-139. The route at `routes/tts.py:68-77` only formats the returned row afterward, without another service/UoW call. Separate poll/voice routes are outside this generate-drain contract; no new universal HTTP-request drain is inferred. F2 is substantively closed.

### R2 — Regressions, old fixtures and the new negative oracles

**No deadlock or lost wake-up is introduced by the specified ordering.** Entry/admission, stop, cancel and `_finish` use `_lock`; caller-finally and predicate inspection use the Condition built over that same lock. `wait_for` releases the lock while asleep, reevaluates the predicate, and handles notification-before-wait correctly. Both reservation release and caller decrement notify under the lock. A worker finishing first leaves callers busy; a caller returning first leaves the reservation busy.

The entry/admission critical sections end before collaborator work and before `spawn`; the caller count does not mean holding a lock throughout the call. `FIXTURE_REPAIRS` (a)'s synchronous `spawn=lambda fn: fn()` can therefore enter cancel or `_finish` without recursive acquisition. The real progress test at `tests/unit/test_services.py:1748-1751` calls cancel during the port body, outside that lock. Its Cancelled result and stored-row response remain intact (D-24). The caller's finally takes the lock only after spawn/get_status has finished.

The entry refusal changes precedence only once the service is closing. Existing TTS validation/model-not-loaded tests never stop that service first, so their current check order remains. The stop calls found elsewhere in `test_services.py:1012,1213,1234,2049` belong to download/transcript services, verified in their bodies. AC-77.3's synchronous validation remains before row creation/spawn. A validation exception also decrements the caller count.

AC-77.1 still returns Generating while the fake port blocks; the count is zero after generate returns, but the worker reservation keeps wait_idle false until its terminal write. TA-7/TA-8 wait after service.generate, TA-9/TA-10 and repair (f) wait after the HTTP POST has returned, so none waits for its own still-active caller. `Stack.wait_idle` at `test_tts_assets.py:155-161` is a different model-download poll and stays unchanged. The stored terminal-row read and all ten previously approved TA scopes remain approved; no additional assertion amendment is authorized.

AC-77.9(a)-(d) retain cancellation, explicit False/teardown refusal, True/unload/dispose ordering and entry refusal. (e)'s deferred worker remains busy by reservation even after its caller returns. (f)'s spawn error remains counted through `_finish`, preserves the stop's Cancelled outcome and releases both ownership components.

For (g), the fake runs the worker to Done, clears the reservation, then holds A inside spawn before its return read. That is precisely the formerly unowned interval. With B's stop arrival observed, the old reservation-only predicate would let B finish while A is held, failing the noncompletion oracle; the corrected predicate waits. The final ordered, locked UoW/stopped list checks the caller's final DB open precedes stop completion. For (h), holding list_voices establishes an entered caller before admission; with stop arrival observed, the old predicate would again return early. The corrected one waits; releasing A yields admission ConflictError/no row; a later generate must make no get_model_status call. Thus the cases specify the right intervals and observable outcomes.

**Boundedness:** plan :144 requires every Event.wait/join/wait_idle/poll to have a ≤5 s timeout and an asserted result. Implement the arrival observations above with asserted bounded events/closing observation; release fakes in cleanup and assert helper completion/exceptions. `join(0.2)` proves noncompletion only after arrival is established. This preserves the round-3 caution rather than escalating it into a new runtime finding. These are planned tests; no execution success is claimed.

### R3 — Census adequacy (PR-6)

**Pass.** The before and after files are complete raw matching lines, not shortened excerpts. Parsed all headings and all **126** source records, then checked every record's full content against the appropriate source: before-plan/task records against the saved pre-edit copies, unchanged script/product/test records against the current tree, and after records against the current tree. Independently repeated **36** complete fixed-string search sections and compared sorted full file:line:content sets, including zero-hit sections. All matched. Separately repeated the before receipt's generate-return-value search: exactly the same six real call sites matched.

Verified all **nine** hashes in sha256.txt, using the saved plan/task copies and current unchanged companion files. Both plan/task no-index diffs were read; only D-31's caller lifetime, the two AC cases, decision carry-forward and correction/receipt text changed. The four scripts remain byte-identical to the snapshot. No census claim substitutes for runtime proof.

The correction log's per-site dispositions match the actual semantic changes: :131/:132/:136/:301 updated; D-31/new correction row added; TA/wait consumers and get_status/generate callers confirmed consistent; D-30 historical entries retained and extended by D-31; model-service and fake get_status hits correctly distinguished. The planning-receipt refresh at :728 is consistent with the log's post-correction receipt-results section. The first local comparison helper stopped on an empty-set PowerShell Compare-Object binding, then was corrected and rerun to completion; this was an inspection-helper error, not a census mismatch.

### R4 — F1 and F3–F8

**No regression found.** The closure table identifies the current contracts and executable producer/consumer evidence. D-31 changes caller drain only. Cancellation atomicity, audit retry/actual-Cancelled oracle, pre/post audit binding, reproducible FIXED comparison, whole-tree gate membership, committed route template and worktree-target resolution remain intact. No closed finding is reopened without new substantive evidence.

## Checklist Results

Manual observations below: **observer gpt-6.1-sol**, **exit_code null**. They are file comparisons and static traces. Passing design checks do not certify implemented product behavior.

### Plan Review checklist

| Check | Result | Observed procedure and evidence |
|---|---|---|
| PR-1 | pass | Compare all 24 task rows with the named contracts and work packages. Order remains MEU-76 → MEU-78 → MEU-77; H1 audit/full gate/review precede H2. |
| PR-2 | pass | Inspect worktree git state, all task statuses and implementation-artifact existence. All 24 implementation rows remain pending; baseline.sha, walkthrough, gate/audit results and three implementation handoffs are absent. |
| PR-3 | pass | Read the task table and compare its structure with the permitted static verifier. All 24 rows have owners, deliverables, exact validation, dependencies, context and durable outputs. |
| PR-4 | pass | Trace validation design and evaluator/runner call chains without executing product checks. AC-77.9 covers timeout, pre-spawn reservation, spawn failure and both caller-drain intervals; execution notes retain arrival synchronization and cap reconciliation. |
| PR-5 | pass | Compare FIC source columns with residual Spec 03:468–494, 04:427–439 and actual service/lifespan behavior. All three MEUs have observable source-backed criteria; D-31 cites reachable pre-admission model/assets calls and the final UoW read. |
| PR-6 | pass | Compare every raw census record to current or snapshot source; repeat complete rg searches; verify hashes and manually reconcile every source site with the correction log. 36 complete section comparisons, all 126 records verified, plus an independent six-hit generate-return search; nine snapshot-manifest hashes match. Semantic dispositions cover the correction. |
| PR-7 | pass | Read Out of Scope, inspect the MEU-72–79 SSOT records and compare with the registered goal. Deferred MEU-72–75/79 exist; shutdown, live resolver, API errors, OpenAPI and tts.cancel remain in scope. |
| PR-8 | pass | Enumerate entry/stop/admission/spawn/finish/return races under the stated lock and Condition. D-31 counts every entered caller through its last collaborator access; D-30 reserves every worker; both predicate components and notifications share one lock. |
| PR-9 | pass | Compare repeated-literal census, named definitions and their AC/task/script references. The live idle predicate is defined in ASYNC_GENERATE; historical D-30 is explicitly extended by D-31, not a competing current definition. |

### Documentation Review checklist

| Check | Result | Observed procedure and evidence |
|---|---|---|
| DR-1 Claim/state match | pass | Compared the pre-edit diff and live contracts with correction claims: caller count, combined predicate and two cases are present; scripts unchanged. |
| DR-2 Residual old terms | pass | Repeated raw census searches; old predicate/range zero hits remain zero; retained D-30 text is historical and explicitly extended. |
| DR-3 Downstream references | pass | task.md H2-1 carries D-8 through D-31; AC references and stored-row/fixture consumers agree. Cap caller note is disclosed above. |
| DR-4 Verification robustness | pass | Read negative oracle designs and independently ran all allowed injected-defect selftests; arrival-signal requirement retained. |
| DR-5 Evidence auditability | pass | Complete permitted-verifier outputs, preserved exits and census comparison below; no scratch-only runtime success assertion. |
| DR-6 Cross-reference integrity | pass | Compared actual service/main/wiring/routes with residual Spec and reconciliation inventory; no feature scope removed. |
| DR-7 Evidence freshness | pass | Round-4 checks rerun at actual c72fc44 state; historical 7861020 receipts not relabelled as current. |
| DR-8 Completion vs residual risk | pass | Plan approval only; tasks pending, product checks not run, execution authorization/S4 remain required. |

### Information Retrieval / template / adversarial checks

| Check | Result | Procedure and evidence |
|---|---|---|
| All AC source labels; exact validation; hub audit; post-MEU rows | pass | Read FICs, plan :360-388 and all task rows; three dated handoffs, hub reconciliation, reflection and metrics are scheduled. |
| Naming/template/frontmatter | pass | REVIEW-TEMPLATE 2.2 read; report uses exactly the user's nine frontmatter keys, round 4 and absolute worktree target. |
| Referenced artifacts | pass | Static verifier checks every Files Modified target; explicit Test-Path checks found all 14 sampled script/config/template dependencies. New tests/handoffs/evidence are scheduled creates, not falsely claimed present. |
| AV-1 / AV-3 design | pass | AC-tagged Red/Green controls, immutable assertions, bounded failure/ordering/cancel oracles and the GUI polling pin are scheduled; D-31 covers F2's missing interval. |
| AV-2 / AV-4 bypass/skip masking | pass | No new bypass/skip prescribed; evaluator negative cases still reject nonassertion/collection/skipped-or-flaky pin failures and missing AC coverage. |
| AV-6 source-backed criteria | pass | D-31 derives from actual collaborator calls and the existing shutdown safety requirement; no new feature scope invented. |
| Completed execution bundle / FAIL_TO_PASS / AV-5 completed code | n/a | This is an unstarted plan; execution evidence remains future work. |

All nine required sweeps were performed: plan/task consistency, readiness, task fields, validation specificity, dependency order, source traceability, scope discipline, referenced-artifact existence and repeated literals.

## Commands Executed and Output

All shell commands used `rtk proxy`, cwd P:/av-kit-wt/backend-robustness, all-stream receipts under C:/Temp/av-kit and immediate `$LASTEXITCODE` preservation before reading/propagating it. Canonical wrapper:

~~~powershell
rtk proxy <command> *> C:/Temp/av-kit/s33-r4-<check>.txt
$reviewExit=$LASTEXITCODE
Get-Content C:/Temp/av-kit/s33-r4-<check>.txt
exit $reviewExit
~~~

### Static inspection command manifest

| Command / actual manual procedure | Exit | Decisive output |
|---|---|---|
| `rtk proxy git log -1 --format='%H %D'` | 0 | HEAD c72fc4436da8534ef613264620b83c3e84e97631; claude/backend-robustness. |
| `rtk proxy git status --short --untracked-files=all` | 0 | Only the rolling review and ten plan-folder artifacts untracked; no tracked modifications. Git warns that the user-global ignore file is not readable. Its contents were not accessed. |
| `rtk proxy git diff --stat` | 0 | Empty output. |
| `rtk proxy git log --oneline 7861020..HEAD` and `git diff --stat 7861020..HEAD` | 0 each | Session 31 merge/closeout history; 49 files changed, 6022 insertions, 84 deletions. |
| `rtk proxy git diff --no-index --unified=0 -- C:/Temp/av-kit/s33-plan-pre-r3-snapshot/implementation-plan.md docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md` | 1 | Expected diff-present exit. D-31 caller count/predicate, AC-77.9(g)/(h), D-31 carry-forward and correction/receipt text. Git emits LF/CRLF advisory warnings. |
| Same no-index command for snapshot/current `task.md` | 1 | Expected diff-present exit. Only H2-1 decision range D-30→D-31. |
| `rtk proxy rg -n '=\s*(service\|tts)\.generate\(' tests/unit/test_services.py packages/api/src/avkit_api/routes/tts.py` (regex alternation unescaped in actual argv) | 0 | Six generate-return sites, reproduced below. |
| `rtk proxy rg -n 'stop_processing\|_closing' tests/unit/test_services.py tests/integration/test_tts_assets.py` (regex alternation unescaped in actual argv) | 0 | :1012,1213,1234,2049; actual bodies identify download/transcript, not stopped-TTS validation cases. |
| `rtk proxy rg -n -A 22` over `^def _generate_with\|^def test_ac_62_11\|^def test_ac_62_16\|^def test_ac_12_5_invalid_progress` in the two TTS test files | 0 | Existing synchronous 500/Done expectations and helper bodies agree with TA-7–TA-10/repair (f). |
| `rtk proxy rg -n -A 4 'id: MEU-(72\|73\|74\|75\|76\|77\|78\|79)$' .agent/context/meu-status.yaml` | 1 | Empty: the too-strict end-anchored lookup was not evidence of missing MEUs. Repeated below with individual terms. |
| `rtk proxy rg -n -A 5 -e MEU-72 -e MEU-73 -e MEU-74 -e MEU-75 -e MEU-76 -e MEU-77 -e MEU-78 -e MEU-79 .agent/context/meu-status.yaml` | 0 | All eight records exist at :1909,1935,1959,1985,2010,2034,2062,2088. |
| `rtk proxy rg -n` for definitions/imports, fingerprint/audit/cap paths across exec_checks.py, validate-task.ps1 and baseline_carry.py | 0 | Located the exact evaluator and runner blocks cited in the closure table; inspected their bodies before accepting the chain. |
| `rtk proxy pwsh -NoProfile -Command` with Get-Content/numbered ranges | 0 | Read protocol first; then AGENTS/GUARDRAILS/PROFILE, rolling history, template, census/log/vocabulary, target files and canon. Relevant numbered ranges: plan 111–149/153–308/310–395/410–482/620–729; TTS service/main/routes full, wiring 1–90; unit tests 1570–1820/1840–1930 plus actual stop bodies; integration 120–205 and rg-located TA cases; Spec 03:468–496 and 04:427–439. |
| Same Get-Content reads for plan_checks.py, evaluator :272–452/509–549/757–780/906–998, runner :147–193/289–338/501–522, baseline_carry.py full | 0 | Stdlib/selftest side-effect boundaries checked; production verbs were read only. |
| Same Get-Content reads for session context, reviewer role, completion-preflight and v2 schema; protocol/template reread before report | 0 | Read-only independent-review/output requirements applied; no implementation or extra verifier run authorized. |
| Raw census receipt reads + full-record replay/Compare-Object + Get-FileHash | 0 on corrected comparison | 36 sections match; 126 records verified; nine hashes match. Initial helper exit 1 was an empty-reference binding issue and was corrected without changing source/census. |
| Get-Content/regex task count + Test-Path + `rtk proxy git diff --name-only 7861020 HEAD -- <all extracted Files Modified paths>` + Get-FileHash | 0 | 24 pending rows; all implementation artifacts absent; all 14 sampled dependencies present; three overlap paths and current six-file hashes below. |
| Completed-receipt Get-Content/ConvertTo-Json assembly | 0 | Read back verifier/census/state outputs for embedding; an empty diff receipt is null, normalized to empty for rendering. No reviewed file changes. |

The first broad rolling-history terminal view was display-truncated, so the round-3 closure/R1–R4/checklist body and correction tail were read again in bounded ranges. Census completeness was established from the entire on-disk raw receipts and full-content comparisons, never from a truncated terminal preview.

### Current readiness and state output

~~~text
Pending task rows: 24
baseline.sha exists: False
walkthrough.md exists: False
mcp-audit-summary.json exists: False
windows-gate-result.json exists: False
.agent/context/handoffs/2026-10-14-backend-robustness-MEU-76-handoff.md exists: False
.agent/context/handoffs/2026-10-14-backend-robustness-MEU-78-handoff.md exists: False
.agent/context/handoffs/2026-10-14-backend-robustness-MEU-77-handoff.md exists: False
tools/export_openapi.py exists: True
tools/lint_task_contract.py exists: True
tools/validate_closeout_artifacts.py exists: True
tools/durable_evidence.py exists: True
tools/meu_status.py exists: True
tools/issue_triage.py exists: True
tools/Invoke-CodexDispatch.ps1 exists: True
docs/execution/reflections/TEMPLATE.md exists: True
.agent/schemas/reflection.v1.yaml exists: True
ui/electron-builder.yml exists: True
ui/package.json exists: True
mcp-server/package.json exists: True
uv.lock exists: True
openapi.committed.json exists: True
Files Modified paths changed since 7861020:
ui/src/renderer/src/features/settings/SettingsPage.tsx
ui/tests/e2e/settings.test.ts
ui/tests/e2e/test-ids.ts
Snapshot changed-file scope:
implementation-plan.md sha256=edc8fdb6f58dc16771f45896898a6781189b46ea8c697a0ad8ff02fdd93ffdba
task.md sha256=f12cacd011815160f4da06a448f6e40ff8cfd3e9cb2630f1ee3166fcdc362980
validate-task.ps1 sha256=10d88f5e38934b18e099603cd359faf80659ef55cd7f62d4e9e3f654e3df6a88
exec_checks.py sha256=9c8853e90fd7b3108cfd6f97e827b1a6f303e27a794f92a76ea92d2124362d8b
plan_checks.py sha256=012518206cd8db1430ede2881820a38cfe9b7bd62bd91c290fc3dbc836ee842f
baseline_carry.py sha256=89130fd81d63c1892ee462f82d8d9e5d7f2d892d4707161066f0fe847f407b0c
~~~

### Generate-return caller sweep output

~~~text
packages/api/src/avkit_api/routes/tts.py:68:    job = tts.generate(
tests/unit/test_services.py:1706:    job = service.generate(
tests/unit/test_services.py:1736:    job = service.generate(
tests/unit/test_services.py:1757:    cancelled = service.generate(
tests/unit/test_services.py:1793:    job = service.generate("hi", "am_eric", 1.0, MediaFormat.WAV, [], TTSSourceKind.Inline, None)
tests/unit/test_services.py:1919:    job = service.generate("hi", "am_eric", 1.0, MediaFormat.WAV, [], TTSSourceKind.Inline, None)
~~~

### Census replay output

~~~text
MATCH before [returns `self.get_status(job.id)` (the row as stored)] records=1
MATCH before [get_status] records=4
MATCH before [lambda: self._current_id is None, timeout] records=1
MATCH before [once no job is reserved] records=1
MATCH before [waits on the reservation, not on a thread] records=1
MATCH before [counts as busy] records=1
MATCH before [D-8 to D-30] records=2
MATCH before [AC-77.9] records=3
MATCH before [wait_idle] records=9
MATCH before [D-30] records=9
MATCH before [notify_all] records=1
MATCH before [_current_id is None] records=1
MATCH before [product/tests: get_status] records=12
MATCH after [returns `self.get_status(job.id)` (the row as stored)] records=1
MATCH after [get_status] records=7
MATCH after [lambda: self._current_id is None, timeout] records=0
MATCH after [once no job is reserved] records=1
MATCH after [waits on the reservation, not on a thread] records=1
MATCH after [counts as busy] records=1
MATCH after [D-8 to D-30] records=0
MATCH after [D-8 to D-31] records=2
MATCH after [AC-77.9] records=4
MATCH after [wait_idle] records=11
MATCH after [D-30] records=7
MATCH after [D-31] records=8
MATCH after [notify_all] records=2
MATCH after [_current_id is None] records=3
MATCH after [_callers] records=4
MATCH after [enters] records=4
MATCH after [a stop can begin after entry] records=1
MATCH after [Caller drain] records=1
MATCH after [never held across] records=1
MATCH after [R3] records=2
MATCH after [round 4 plan review] records=1
MATCH after [product/tests: _callers] records=0
MATCH after [product/tests: get_status] records=12
PASS census: 36 complete section comparisons; 126 source records verified
HASH MATCH docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md
HASH MATCH docs/execution/plans/2026-10-14-backend-robustness/review-prompt-plan.md
HASH MATCH docs/execution/plans/2026-10-14-backend-robustness/review-r1-census.md
HASH MATCH docs/execution/plans/2026-10-14-backend-robustness/review-r2-census.md
HASH MATCH docs/execution/plans/2026-10-14-backend-robustness/task.md
HASH MATCH docs/execution/plans/2026-10-14-backend-robustness/baseline_carry.py
HASH MATCH docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py
HASH MATCH docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py
HASH MATCH docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1
~~~

The replay parsed every raw section and compared full source records. For before plan/task lookups it substituted only the source file with the snapshot copy, preserving original file:line prefixes; other lookups used the actual worktree. It sorted complete record sets only after rg finished. SHA256 checks used the snapshot plan/task and unchanged current companions. The six-callsite return sweep above covers the sole nonliteral section separately.

### Permitted plan-local verifiers


**Command:** `rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static` — **exit 0**.

~~~text
PASS static: 24 task rows; script, exec_checks, plan contracts, references and file targets agree
~~~

**Command:** `rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py selftest` — **exit 0**.

~~~text
PASS selftest duplicate row id: duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6',
PASS selftest unknown check: task.md invokes -Check 'no-such-check', which validate-task.ps1 does not define
PASS selftest swapped stage: stage order differs: ps1=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-bui
PASS selftest gate exclusion added: GATED_PATHS differ: plan GATE_EXCLUDED=['.agent/context/meu-status.yaml', '.agent/context/meu-registry.md', '.agent/context/current-focus.md
PASS selftest ps1 gated copy: GATED_PATHS differ: validate-task.ps1 holds its own $gated copy
PASS selftest changed floor: COUNT_FLOORS differ: plan={'pytest': 600, 'vitest': 773, 'e2e': 133} exec_checks={'pytest': 655, 'vitest': 773, 'e2e': 133}
PASS selftest AC tier changed: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'
PASS selftest AC row dropped: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'
PASS selftest pin dropped: pins differ: plan=set() exec_checks={'77.14'}
PASS selftest TA file changed: TEST_AMENDMENTS differ: plan={1: 'tests/unit/test_domain.py', 2: 'tests/integration/test_filesystem_media.py', 3: 'tests/unit/test_domain.py
PASS selftest source audit file dropped: $SRC76 differs from product_files: ps1-only={'x.ts'} plan-only={'ui/src/renderer/src/lib/api.ts'}
PASS selftest red without guard: red78 does not start with the red-guard
PASS selftest TA in red: red77 runs a TEST_AMENDMENTS array (TAs apply only in Green)
PASS selftest undefined AC: task.md references AC-78.99, which has no definition site
PASS selftest undefined D: task.md references D-99, which has no definition site
PASS selftest undefined TA: task.md references TA-11, which has no definition site
PASS selftest missing modify target: Files Modified 'modify' row names a missing file: ui/no/such/file.ts
PASS selftest existing create target: Files Modified 'create' row names a file that already exists: pyproject.toml
PASS selftest missing goal anchor: review-prompt-plan.md does not contain the Goal sentence (INTENT_BINDING)
PASS selftest: every injected defect was reported
~~~

**Command:** `rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py selftest` — **exit 0**.

~~~text
ok  pytest red76 good: PASS (expected PASS)
  ok  pytest red76 with a NEG_MARK pass: PASS (expected PASS)
  ok  pytest red76 TypeError (non-assertion): FAIL (expected FAIL) - non-assertion failure: tests.unit.test_x::test_ac_76_7_x: TypeError: unexpected keyword 's
  ok  pytest red76 missing AC-76.7: FAIL (expected FAIL) - AC-76.7 has no decisive assertion failure in pytest
  ok  pytest red76 tagged pass without NEG_MARK: FAIL (expected FAIL) - tagged test passed in Red (no NEG_MARK): tests.unit.test_x::test_ac_76_1_extra
  ok  pytest red76 untagged failure: FAIL (expected FAIL) - untagged test did not pass (failed): tests.unit.test_x::test_old_breaks
  ok  pytest red76 collection error: FAIL (expected FAIL) - collection error ::tests.unit.test_x: ImportError: x
  ok  pytest red76 ac_76_10 is not AC-76.1: FAIL (expected FAIL) - tests.unit.test_x::test_ac_76_10_x: AC-76.10 is not an AC of MEU-76
  ok  pytest red76 exit 0: FAIL (expected FAIL) - Red run exited 0
  ok  pytest red76 DID NOT RAISE counts: PASS (expected PASS)
  ok  vitest red76 good: PASS (expected PASS)
  ok  vitest red76 load error: FAIL (expected FAIL) - load error x.test.ts: Failed to resolve import
  ok  vitest red76 TypeError: FAIL (expected FAIL) - non-assertion failure: api AC-76.8 x: TypeError: Cannot read properties of undefined
  ok  vitest red76 AC-76.80 not AC-76.8: FAIL (expected FAIL) - AC-76.80 x: AC-76.80 is not an AC of MEU-76
  ok  mcp red76 jest-dom style expect: PASS (expected PASS)
  ok  electron red78 good: PASS (expected PASS)
  ok  electron red78 test timeout: FAIL (expected FAIL) - non-assertion failure: f.ts > AC-78.9 x: Test timeout of 30000ms exceeded.
  ok  electron red78 top-level error: FAIL (expected FAIL) - top-level error: Error: launch failed
  ok  electron red77 pin passes: PASS (expected PASS)
  ok  electron red77 pin fails: FAIL (expected FAIL) - pin test must pass in Red (failed): f.ts > AC-77.14 x
  ok  electron red77 pin flaky: FAIL (expected FAIL) - pin test must pass in Red (flaky): f.ts > AC-77.14 x
  ok  pytest green77 needs every AC: FAIL (expected FAIL) - AC-77.10 has no passing test in pytest
  ok  pytest green77 good: PASS (expected PASS)
  ok  pytest green77 a failure: FAIL (expected FAIL) - exit 1
  ok  fingerprint lines sorted, content-bound, deletions recorded
  ok  GATED_PATHS ui/src/x.ts: gated
  ok  GATED_PATHS .agent/workflows/mcp-audit.md: gated
  ok  GATED_PATHS .agent/docs/commands.md: gated
  ok  GATED_PATHS docs/execution/plans/TASK-TEMPLATE.md: gated
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md: gated
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/baseline_carry.py: gated
  ok  GATED_PATHS .agent/skills/mcp-tool-audit/resources/baseline-snapshot.json: gated
  ok  GATED_PATHS .agent/context/meu-status.yaml: excluded
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/windows-gate-result.json: excluded
  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/task.md: excluded
  ok  GATED_PATHS .agent/context/handoffs/2026-10-14-backend-robustness-MEU-77-handoff.md: excluded
  ok  GATED_PATHS .agent/context/handoffs/2026-09-26-framework-update-adoption-implementation-critical-review.md: gated
  ok  audit fp good: PASS
  ok  audit fp moved during the audit: FAIL
  ok  audit fp tree changed after: FAIL
  ok  audit fp missing before: FAIL
  ok  openapi allowed change: PASS
  ok  openapi added path: FAIL
  ok  openapi other schema: FAIL
  ok  openapi other path: FAIL
  ok  openapi job route by its committed template {id}: PASS
  ok  audit good: PASS
  ok  audit cancel not FIXED: FAIL
  ok  audit regression: FAIL
  ok  audit cleanup failed: FAIL
  ok  audit baseline misses an action: FAIL
  ok  audit baseline commit drift: FAIL
  ok  gate good: PASS
  ok  gate tree changed after: FAIL
  ok  gate stage order: FAIL
  ok  gate e2e flaky: FAIL
  ok  gate pytest under carried floor: FAIL
  ok  gate mcp under row-0 floor: FAIL
  ok  gate fingerprint moved in run: FAIL
  ok  review good: PASS
  ok  review absolute worktree target: PASS
  ok  review other checkout target: FAIL
  ok  review self-authored agent: FAIL
  ok  review changes_required: FAIL
  ok  review over cap: FAIL
PASS selftest
~~~

All 19 plan-local injected-defect cases and all 65 evaluator cases reported their expected outcomes. These outputs are tooling evidence, not tests of a delivered implementation.

### Durable evidence

~~~json
{"schema_version":"evidence.v1","check_id":"s33-r4-static","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py static","cwd":"P:/av-kit-wt/backend-robustness","scope":"permitted plan-local static","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; plan SHA256 edc8fdb6f58dc16771f45896898a6781189b46ea8c697a0ad8ff02fdd93ffdba; four scripts match pre-round-3 manifest","output":"PASS static: 24 task rows; script, exec_checks, plan contracts, references and file targets agree","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-r4-plan-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/plan_checks.py selftest","cwd":"P:/av-kit-wt/backend-robustness","scope":"permitted plan-local plan-selftest","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; plan SHA256 edc8fdb6f58dc16771f45896898a6781189b46ea8c697a0ad8ff02fdd93ffdba; four scripts match pre-round-3 manifest","output":"PASS selftest duplicate row id: duplicate row ids: ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'H1-1', 'H1-2', 'H1-3', 'H1-4', 'H1-5', 'H1-6',\r\nPASS selftest unknown check: task.md invokes -Check 'no-such-check', which validate-task.ps1 does not define\r\nPASS selftest swapped stage: stage order differs: ps1=['npm-ci', 'mcp-npm-ci', 'py-lint', 'py-types', 'ui-types', 'ui-lint', 'mcp-types', 'py-tests', 'ui-tests', 'ui-bui\r\nPASS selftest gate exclusion added: GATED_PATHS differ: plan GATE_EXCLUDED=['.agent/context/meu-status.yaml', '.agent/context/meu-registry.md', '.agent/context/current-focus.md\r\nPASS selftest ps1 gated copy: GATED_PATHS differ: validate-task.ps1 holds its own $gated copy\r\nPASS selftest changed floor: COUNT_FLOORS differ: plan={'pytest': 600, 'vitest': 773, 'e2e': 133} exec_checks={'pytest': 655, 'vitest': 773, 'e2e': 133}\r\nPASS selftest AC tier changed: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'\r\nPASS selftest AC row dropped: AC tables differ from exec_checks.ACS: plan={'76': {'76.1': 'pytest', '76.2': 'pytest', '76.3': 'pytest', '76.4': 'pytest', '76.5': 'pytest'\r\nPASS selftest pin dropped: pins differ: plan=set() exec_checks={'77.14'}\r\nPASS selftest TA file changed: TEST_AMENDMENTS differ: plan={1: 'tests/unit/test_domain.py', 2: 'tests/integration/test_filesystem_media.py', 3: 'tests/unit/test_domain.py\r\nPASS selftest source audit file dropped: $SRC76 differs from product_files: ps1-only={'x.ts'} plan-only={'ui/src/renderer/src/lib/api.ts'}\r\nPASS selftest red without guard: red78 does not start with the red-guard\r\nPASS selftest TA in red: red77 runs a TEST_AMENDMENTS array (TAs apply only in Green)\r\nPASS selftest undefined AC: task.md references AC-78.99, which has no definition site\r\nPASS selftest undefined D: task.md references D-99, which has no definition site\r\nPASS selftest undefined TA: task.md references TA-11, which has no definition site\r\nPASS selftest missing modify target: Files Modified 'modify' row names a missing file: ui/no/such/file.ts\r\nPASS selftest existing create target: Files Modified 'create' row names a file that already exists: pyproject.toml\r\nPASS selftest missing goal anchor: review-prompt-plan.md does not contain the Goal sentence (INTENT_BINDING)\r\nPASS selftest: every injected defect was reported","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-r4-exec-selftest","command":"rtk proxy python docs/execution/plans/2026-10-14-backend-robustness/exec_checks.py selftest","cwd":"P:/av-kit-wt/backend-robustness","scope":"permitted plan-local exec-selftest","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; plan SHA256 edc8fdb6f58dc16771f45896898a6781189b46ea8c697a0ad8ff02fdd93ffdba; four scripts match pre-round-3 manifest","output":"ok  pytest red76 good: PASS (expected PASS)\r\n  ok  pytest red76 with a NEG_MARK pass: PASS (expected PASS)\r\n  ok  pytest red76 TypeError (non-assertion): FAIL (expected FAIL) - non-assertion failure: tests.unit.test_x::test_ac_76_7_x: TypeError: unexpected keyword 's\r\n  ok  pytest red76 missing AC-76.7: FAIL (expected FAIL) - AC-76.7 has no decisive assertion failure in pytest\r\n  ok  pytest red76 tagged pass without NEG_MARK: FAIL (expected FAIL) - tagged test passed in Red (no NEG_MARK): tests.unit.test_x::test_ac_76_1_extra\r\n  ok  pytest red76 untagged failure: FAIL (expected FAIL) - untagged test did not pass (failed): tests.unit.test_x::test_old_breaks\r\n  ok  pytest red76 collection error: FAIL (expected FAIL) - collection error ::tests.unit.test_x: ImportError: x\r\n  ok  pytest red76 ac_76_10 is not AC-76.1: FAIL (expected FAIL) - tests.unit.test_x::test_ac_76_10_x: AC-76.10 is not an AC of MEU-76\r\n  ok  pytest red76 exit 0: FAIL (expected FAIL) - Red run exited 0\r\n  ok  pytest red76 DID NOT RAISE counts: PASS (expected PASS)\r\n  ok  vitest red76 good: PASS (expected PASS)\r\n  ok  vitest red76 load error: FAIL (expected FAIL) - load error x.test.ts: Failed to resolve import\r\n  ok  vitest red76 TypeError: FAIL (expected FAIL) - non-assertion failure: api AC-76.8 x: TypeError: Cannot read properties of undefined\r\n  ok  vitest red76 AC-76.80 not AC-76.8: FAIL (expected FAIL) - AC-76.80 x: AC-76.80 is not an AC of MEU-76\r\n  ok  mcp red76 jest-dom style expect: PASS (expected PASS)\r\n  ok  electron red78 good: PASS (expected PASS)\r\n  ok  electron red78 test timeout: FAIL (expected FAIL) - non-assertion failure: f.ts > AC-78.9 x: Test timeout of 30000ms exceeded.\r\n  ok  electron red78 top-level error: FAIL (expected FAIL) - top-level error: Error: launch failed\r\n  ok  electron red77 pin passes: PASS (expected PASS)\r\n  ok  electron red77 pin fails: FAIL (expected FAIL) - pin test must pass in Red (failed): f.ts > AC-77.14 x\r\n  ok  electron red77 pin flaky: FAIL (expected FAIL) - pin test must pass in Red (flaky): f.ts > AC-77.14 x\r\n  ok  pytest green77 needs every AC: FAIL (expected FAIL) - AC-77.10 has no passing test in pytest\r\n  ok  pytest green77 good: PASS (expected PASS)\r\n  ok  pytest green77 a failure: FAIL (expected FAIL) - exit 1\r\n  ok  fingerprint lines sorted, content-bound, deletions recorded\r\n  ok  GATED_PATHS ui/src/x.ts: gated\r\n  ok  GATED_PATHS .agent/workflows/mcp-audit.md: gated\r\n  ok  GATED_PATHS .agent/docs/commands.md: gated\r\n  ok  GATED_PATHS docs/execution/plans/TASK-TEMPLATE.md: gated\r\n  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md: gated\r\n  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/baseline_carry.py: gated\r\n  ok  GATED_PATHS .agent/skills/mcp-tool-audit/resources/baseline-snapshot.json: gated\r\n  ok  GATED_PATHS .agent/context/meu-status.yaml: excluded\r\n  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/windows-gate-result.json: excluded\r\n  ok  GATED_PATHS docs/execution/plans/2026-10-14-backend-robustness/task.md: excluded\r\n  ok  GATED_PATHS .agent/context/handoffs/2026-10-14-backend-robustness-MEU-77-handoff.md: excluded\r\n  ok  GATED_PATHS .agent/context/handoffs/2026-09-26-framework-update-adoption-implementation-critical-review.md: gated\r\n  ok  audit fp good: PASS\r\n  ok  audit fp moved during the audit: FAIL\r\n  ok  audit fp tree changed after: FAIL\r\n  ok  audit fp missing before: FAIL\r\n  ok  openapi allowed change: PASS\r\n  ok  openapi added path: FAIL\r\n  ok  openapi other schema: FAIL\r\n  ok  openapi other path: FAIL\r\n  ok  openapi job route by its committed template {id}: PASS\r\n  ok  audit good: PASS\r\n  ok  audit cancel not FIXED: FAIL\r\n  ok  audit regression: FAIL\r\n  ok  audit cleanup failed: FAIL\r\n  ok  audit baseline misses an action: FAIL\r\n  ok  audit baseline commit drift: FAIL\r\n  ok  gate good: PASS\r\n  ok  gate tree changed after: FAIL\r\n  ok  gate stage order: FAIL\r\n  ok  gate e2e flaky: FAIL\r\n  ok  gate pytest under carried floor: FAIL\r\n  ok  gate mcp under row-0 floor: FAIL\r\n  ok  gate fingerprint moved in run: FAIL\r\n  ok  review good: PASS\r\n  ok  review absolute worktree target: PASS\r\n  ok  review other checkout target: FAIL\r\n  ok  review self-authored agent: FAIL\r\n  ok  review changes_required: FAIL\r\n  ok  review over cap: FAIL\r\nPASS selftest","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-r4-lifecycle","procedure":"Trace all generate caller/worker ownership intervals and the Condition predicate, then compare with actual collaborator call sites and AC-77.9.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/backend-robustness","scope":"F2/R1/R2","phase":"planning","exit_code":null,"result":"pass","tested_state":"D-31 plan at c72fc44; plan SHA256 edc8fdb6f58dc16771f45896898a6781189b46ea8c697a0ad8ff02fdd93ffdba","output":"Entry-to-finally caller count covers model/voice/assets prechecks and post-spawn UoW read; worker reservation covers admission through final collaborator access; True requires both drained and False skips teardown. F2 closed.","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-r4-census","procedure":"Parse complete raw before/after receipts; compare each source record; repeat literal rg searches; compare six generate-return callers; reconcile dispositions; verify snapshot manifest hashes.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/backend-robustness","scope":"PR-6","phase":"planning","exit_code":null,"result":"pass","tested_state":"round-3 correction and current round-4 reviewed tree","output":"36 complete literal-search sections match; all 126 records agree with their sources; six generate-return sites match; nine manifest hashes match; scripts unchanged and semantic siblings dispositioned.","fresh":true}
{"schema_version":"evidence.v1","check_id":"s33-r4-product-execution","procedure":"Honor static-only review and run only the three explicitly permitted plan-local verifier verbs.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/backend-robustness","scope":"product execution","phase":"planning","exit_code":null,"result":"not_run","tested_state":"unstarted Session 33 plan","output":"No tests, builds, generators, validate-task checks or MCP audit were run; no product runtime success claimed."}
~~~

## Open Questions / Assumptions / Residual Risk

No unresolved design question prevents plan approval. Correctness still depends on implementing the stated lock/Condition/finally ordering and the bounded arrival assertions, then producing actual Red/Green, contract, Electron and authoritative audit evidence. External collaborator failures, failed unlink cleanup and the previously disclosed fingerprint endpoint/exclusion limits remain execution risks; they are not reopened here.

Execution is not presently certified: it still requires the direct user execution message, the stale cap caller's reconciliation and S4 disposition of the merged base. No different checkout was examined. The completion-preflight skill was consulted for canonical task state and review-artifact completeness; its execution-persistence language does not authorize this reviewer to implement the 24 pending rows.

## Verdict

**approved** — executing the corrected behavioral plan would deliver the registered intent. D-31 closes F2's remaining caller-tail gap and also covers pre-admission collaborator accesses. F1–F8 are all closed; PR-6 and the three permitted verifiers pass. **Intent achieved: yes at plan level**, with zero new findings and the non-blocking execution notes above.

Matching v2 verdict summary:

Approved: D-31 closes F2; F1–F8 are closed, PR-6 passes, and all three permitted verifiers pass. Non-blocking execution notes: reconcile prereq's stale cap 3 with Mat's authorized cap 4, reconcile the observed c72fc44 base under S4, and retain asserted stop-arrival barriers in concurrency tests. Report: C:/Temp/av-kit/dispatch/s33-plan-review-report.md.

## Follow-Up Actions

1. Dispatcher appends this complete report verbatim to the canonical rolling review and records the matching v2 verdict in **s33-plan-2026-10-14-backend-robustness**, **round 4**. Preserve the prior reports and Mat's continuation.
2. Before execution, reconcile the prereq cap caller with the authorized cap 4 and use the existing S4/human-decision procedure for the three merged-base overlap paths. Obtain/record the required direct execution authorization; this review supplies none.
3. During authorized implementation, realize AC-77.9(f)–(h) with asserted bounded caller/stop arrival signals, then run the plan's required validation/audit flow. Preserve TA-1–TA-10's exact approved scopes.
4. **End this plan-review loop.** Round 4 is the last permitted round and it is approved; no additional corrective review, ledger reset, product implementation, commit or push is performed by this reviewer.

Report: **C:/Temp/av-kit/dispatch/s33-plan-review-report.md**.

Canonical destination (dispatcher-owned): **P:/av-kit-wt/backend-robustness/.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md**.
