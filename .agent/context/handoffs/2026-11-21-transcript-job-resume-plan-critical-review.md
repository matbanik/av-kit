---
date: "2026-11-21"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-21-transcript-job-resume/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "tjr-plan2-2026-11-21-transcript-job-resume"
round: 1
---

# Critical Review: 2026-11-21-transcript-job-resume

> **Review Mode:** plan
> **Verdict:** approved

## Scope

**Target:** the complete working-tree implementation plan and task table for Session 101, MEU-163, including Mat's defaults addition. HEAD is `159e178`.

**Review Type:** independent read-only review by Codex, class `avkit_independent_reviewer`; Claude Code, vendor Anthropic, authored the plan.

**Checklist Applied:** PR-1 to PR-9, source tracing, test/default dependency searches, and Q1 to Q6. D-1350, D-1351 and D-1355 and the disclosed autonomous decision authority were accepted as instructed. Loop 1 used one round; its F1 is rechecked under Q2 without becoming a finding in this loop.

All writes were under `C:/Temp/av-kit`. No repository edits, package manager, product suite, backend, Electron launch, network request, commit or push occurred. Supplied planning receipts were inspected; their test runs were not reproduced. The disclosed host-ignore difference was excluded from conclusions, and the file it hides was not opened. Forbidden secret paths and Mat's app data were not opened.

## Intent Anchor

when a transcript job is `Paused` and no job is running, the job's card offers **Resume** first in its three-dot menu. A click sends the existing bodyless `POST /transcripts/resume`, and the job runs to the end. This works after an app restart, when the processor is `Idle`, which is the case the page cannot handle today. While a job runs, no card offers Resume, and the service refuses a resume (409), so a Paused job never becomes a second running job. The shipped transcript defaults become Mat's values: 20 requests an hour, 120 s between requests, 1 attempt, a 7 s retry delay, batches of 5 and 500 s between batches, in the core settings table, the MCP settings schema and the 06 defaults table. The toolbar, Start, the API routes, OpenAPI and the MCP tools stay as they are. Vitest, pytest and Electron tests prove it, one Electron test on the real backend with a seeded database. There is no manual check.

Intent achieved: **yes**, at the plan-specification level. Implementation remains unstarted: all 27 task rows are unchecked, and the five new product test/fixture files are absent. No High or Critical delivery defect was found.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Goal coverage

Accepted: every goal clause has an observable AC and an implementation/proof row.

| Goal clause | AC | Task rows |
|---|---|---|
| First Paused card offers Resume first; no Resume while Processing | AC-163.1, .2, .3, .7 | 2, 3, 5, 6 |
| One bodyless resume POST from the clicked card | AC-163.3, .4, .7 | 2, 3, 5, 6 |
| Stored Paused plus fresh Idle reaches Done and writes outputs | AC-163.6, .8 | 1, 3, 4, 6 |
| Service refuses while Processing without changing jobs | AC-163.6 | 1, 4 |
| Six defaults in core, MCP schema and 06; stored values retained | AC-163.10 | 3a, 4a, 7 |
| Toolbar, Start, routes, OpenAPI and MCP tools preserved | AC-163.3, .5; scope/hash checks | 4, 4a, 5, 6, H1-2, H1-4 |

The index is covered by AC-163.9/row 7. The plan and task agree on Red before product changes, service/defaults/renderer Green, Electron proof and canon updates. No requested work is silently deferred, and there is no manual acceptance row. Nothing material is rejected under Q1.

## Q2 — Rule, menu, command and loop 1 F1

**Loop 1 F1 is closed in this plan.** CARD_RESUME_COMMAND now requires an uncached GET, parses and publishes its envelope, checks the selected id on that response and invalidates in `finally` (`implementation-plan.md:141`). AC-163.4 explicitly distinguishes cache from backend order and state (`:216`; task row 2 at `task.md:47`). The independent contract model exercised reorder, removal, cached Processing/live Idle, live Processing and POST 409: the first two produced no POST, live Idle permitted one bodyless POST, and 409 propagated with invalidation. This is a model of the proposed contract, not execution of an implemented command.

Accepted: renderer order is the API array order (`TranscriptPage.tsx:180`), supplied by `get_queue` and SQL `queue_position.asc()` (`transcript.py:131`; `repositories.py:176`). Resume scans that same order for the first Paused job (`transcript.py:245`). `_next_job` can run an earlier Pending job first while retaining the resumed Processing selection (`:472`); that existing ordering is explicitly scoped. `processorState !== 'Processing'` allows both Idle/restart and Paused/toolbar states. `resume-job-btn` is distinct from `resume-btn`, and CARD_RESUME_MENU leaves Paused face links empty.

Residual limit: GET and POST are separate operations. RESUME_GUARD bounds a concurrent start by refusing the POST with 409; the endpoint still chooses its current first Paused job. It does not atomically bind the request to the clicked id if another client reorders/removes jobs between requests. That short concurrency window remains an accepted limitation of the explicitly retained bodyless route; it is not the fixed cache-only decision of F1. No new finding is raised on that same surface.

## Q3 — Service guard

Accepted: RESUME_GUARD is first under the existing lock, before the queue read, transition or flags (`implementation-plan.md:142`; `task.md:51`). Start sets Processing under the same lock (`transcript.py:220`), and worker exits coordinate with it. An isolated execution of the production resume AST reproduced the current defect (two Processing rows); adding the exact proposed guard refused Processing without job changes and still accepted Idle and Paused. No worker or database was launched for that probe.

Startup recovery only changes stored Processing jobs (`main.py:46`; `transcript.py:361`), so Paused survives a restart. The unchanged API delegates to this method and maps ConflictError to 409; MCP posts to that same route. Row 1's held caption call keeps the Pending job Processing while resume is attempted; absent the guard the call returns and `pytest.raises` reports `DID NOT RAISE`. The bounded event wait and `finally` stop/release/join avoid a stranded held call (`test_services.py:1139`; `task.md:46`). The supplied guard probe shows 34 passed, 88 deselected. Nothing material is rejected under Q3.

## Q4 — Electron tests and paused fixture

Accepted: PAUSED_FIXTURE uses production `build_services(app_data=...)`, which opens `<app_data>/avkit.db` (`wiring.py:133`); the backend resolves the same database through AVKIT_APP_DATA (`database/engine.py:36`). The raw Done item's path, job output directory, slug and expected compiled/ZIP paths match `_write_volumes` and `_zip_raw` (`transcript.py:380`, `:416`). `transcripts_done: 1` is the API aggregate produced by the seeded Done item (`routes/transcripts.py:40`), rather than an additional TranscriptJob constructor field.

The one item is already Done. `_run_parent` filters Pending items before its loop (`transcript.py:514`), so this fixture performs no caption request, per-request delay, retry delay or batch pause under either defaults set. It proceeds to real compile/ZIP creation. The 30-second bound therefore does not need pacing overrides. The supplied seed receipt shows Idle to Done with both output types; the planned real-backend test adds the actual card click, poll, count, paths and open-zip-link assertions.

Row 3 checks the fixture first and refuses a nonempty/outside-temp target. Both Electron Reds open the existing menu and compare its ordered ids immediately, naming `resume-job-btn`, rather than waiting for that absent item. Seed/launch/timeout failures cannot count as Red. The launch and teardown shapes use scratch profiles, a live close set, the Electron child handle and backend pid plus matching start time (`queue-cancel-paused.test.ts:134`, `:169`, `:194`, `:209`). The seeded transcript database and output files stay under scratch app data. No separate fixture or Electron delivery defect was found; these remain implementation obligations because the files do not yet exist.

## Q5 — Defaults and the three existing test edits

Accepted: TRANSCRIPT_DEFAULTS correctly maps `300→20`, `6→120`, `3→1`, `30→7`, `50→5`, `300→500` in the core and MCP rows. The settings types, bounds, Zod input schema, other keys and namespaces stay unchanged (`settings.py:69`; `settings.ts:34`). DEFAULTS_CANON changes 06's third cells and attributes each new value in its fourth cell while retaining the old value/source; the existing 0 and 490000 remain. SettingsService returns a table default only for a missing stored row (`settings.py:221`), and AC-163.10 checks both default and saved-value behavior. The MCP test checks the same eight numeric leaves; row 4a's build emits updated `dist/` (`mcp-server/package.json:8`; `tsconfig.json:6`). H1-4's two-path hash comparison is appropriate for source/test scope and excludes generated ignored output as intended.

The independent probe executed the production pacing `if index > 0` AST for 400 items. It confirmed the supplied rate result: maximum 18 starts in a rolling hour, 16.44/hour over 399 intervals, and 5.94 hours to request 100. Thus the AC-116.5 single-channel workload still needs no cap waits. **Non-blocking wording correction:** DEFAULTS_CANON at `implementation-plan.md:155` should say a pause *after each five requests, before the next request*. Actual first starts are `0, 120, 240, 360, 480, 1100`; the pause is before request 6, then 11, not “before every 5th request.” The numerical values and planned implementation are unambiguous.

DEFAULTS_TEST_EDITS preserve the properties: AC-116.5 still uses shipped defaults and permits only pacing sleeps; AC-116.9 explicitly restores MEU_116_PACING and retains its cap/retry assertions; AC-122.12 disables the unrelated cap while retaining the request-count assertions. Row 3a proves the latter two setups on today's defaults while requiring assertion Reds for the new defaults tests and AC-116.5. `named-edits` compares all top-level nodes and exact permitted forms, complementing the existing pins and immutable post-Red hashes (`implementation-plan.md:310`; `task.md:44`, `:49`).

The search covered `tests/`, `ui/tests/`, `ui/src/` and MCP source/tests. Other old numbers are explicit mocks/settings or unrelated numeric inputs; no additional default-dependent break was identified. Independent mapping confirmed all 3339 full-probe positions: 3291 dots and 48 failures, comprising exactly the three named defaults failures plus 45 failures in the two closeout files. Their separate no-plugin receipts show 45 failures without UTF-8 and 101 passes with it; the targeted defaults receipt shows 3 failed and 198 passed, and the rewritten-form receipts show 5 passed on new defaults and 2 failed/3 passed on old defaults. This is sufficient planning evidence for the edit set. The hung full probe is **not** a successful full gate; H1-2 requires a fresh completed run after implementation.

The broad “cap delays nothing” prose is not a universal multi-job guarantee: pacing indexes restart per parent, whereas request history spans parents (`transcript.py:514`, `:686`). The 18/hour calculation establishes the continuous-channel workload used by AC-116.5. No queue-wide pacing change is required by this goal.

## Q6 — Pins, session gate and register updates

Accepted: the direct menu/toolbar pins are named, including AC-55.3/.5, the page rules, AC-51.6, test-id prefix and gui-actions audit (`implementation-plan.md:174`). AC-55.5's seed has no Paused card (`transcript-page.behavior.test.ts:49`), so its menu expectations remain valid. The gui-actions audit has no transcript-card-id census; a Palette `no` index row does not change the palette set. Searches also found additional page/canon consumers, including queue-primitives, help-card, icon-hints, capture/convert page canon, queue-canon and help-quick-start. These need no changed assertions and run in full Vitest. The pin table is not a literal inventory of every indirect consumer, but this does not omit their execution or create a materially missing deliverable.

H1-2 covers UI tsc and ESLint, targeted/full Vitest and pytest, pyright, ruff, MCP typecheck/tests/build, OpenAPI comparison, UI build, both Electron files, line endings, home-path, pins, exact defaults edits, Red hashes, scope and input identity (`implementation-plan.md:330`; `task.md:59`). Electron clears ELECTRON_RUN_AS_NODE and checks host load. The explicitly scoped E2E/audit omissions do not remove a requested proof. H2-2 reruns canon tests after its status render.

Row 7 uses the copied `issue-resolve.py` bound to the register hash; its source imports `issue_triage.model` and holds a Windows handle against concurrent writes. It then regenerates known-issues Markdown with issue_triage and updates/renders MEU state with meu_status (`task.md:56`; copy source `issue-resolve.py:20`, `:50`). The copy sources and checked repository tools exist; absent plan-local scripts are expressly assigned creation rows. No invented validator or hand edit of a generated register is needed.

## Checklist Results

| Check | Result | Observed evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Ten dotted ACs map to the same resume/defaults work and dependency order. |
| PR-2 Not started | pass | HEAD 159e178; 27 of 27 task rows unchecked; five new product test/fixture paths absent; product paths clean. |
| PR-3 Task contract | pass | All numbered rows include owner, deliverable, validation and status. |
| PR-4 Validation realism | pass | Specific assertion Reds, completed Green obligations, real-backend outputs, defaults checks and fresh full gate. |
| PR-5 Source-backed planning | pass | Mat's requests, D-1350 to D-1357 and cited service/card canon support the behavior. |
| PR-6 Correction readiness | pass | Single-MEU handoff and independent correction route named; current loop round 1; prior loop F1 explicitly closed in Q2. |
| PR-7 Scope discipline | pass | No requested restart, guard, defaults or real-backend proof is deferred. |
| PR-8 Reachability and negative oracles | pass | Renderer-to-route/service chain, state guard and fixture output producers traced; baseline guard defect reproduced in isolation. |
| PR-9 Named contracts | pass | The nine named contracts govern the rows; no materially ambiguous competing implementation rule. Batch wording correction is non-blocking. |
| AV-1 to AV-6, at plan level | pass | Planned Red/Green evidence, immutable expectations, explicit assertions, no new skip/xfail or placeholder deliverable, source-backed ACs. |
| Product execution validation | n/a | Forbidden in this read-only plan review; no product-suite pass is claimed. |

Manual procedure for the pass rows: compare the complete current plan/task with the cited production code, tests, canon, decision sources, allowed planning receipts and searches; check each AC's producer and negative oracle. Observer: `codex-independent-reviewer`; exit code: null.

```json
{"schema_version":"evidence.v1","check_id":"plan2-independent-probes","command":"rtk proxy python -B C:/Temp/av-kit/2026-11-21-transcript-job-resume/review2/probe.py","cwd":"P:/av-kit","scope":"production pacing/resume AST in stdlib stand-ins, proposed command contract model, supplied full-probe position mapping and declared path checks; no product imports, processes or network","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"HEAD 159e178; implementation-plan sha256 6ae9233303233e8321af2bb54760bcead919ba0b93851f56ff4fd72757204dd8; task sha256 7510c2e745faad828be0d23df934a20129880354573bdccba6b94579eec63373","output":"pacing starts [0,120,240,360,480,1100,1220]; busiest rolling hour 18; 399-interval average 16.44/hour; 100-item time 5.94h. Full probe 3339/3339 positions: 3291 dots, 48 F; only non-closeout failures AC-116.5, AC-116.9 and AC-122.12[50]. Contract model: reordered/removed id no POST; cached Processing/live Idle one bodyless POST; 409 rejects and invalidates. Baseline resume AST returns two Processing jobs; proposed guard refuses Processing unchanged and accepts Idle/Paused. 27/27 task rows unchecked; five new product test/fixture paths absent; checked copy sources and gate tools exist.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"plan2-source-trace","procedure":"Read the complete plan/task and named production/service/settings/Electron/test/canon sources, search defaults and pins across tests, UI and MCP, inspect only named planning receipts, and compare each Q1-Q6 obligation to its AC and row.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 101 MEU-163 plan and its cited dependencies","phase":"plan-review","exit_code":null,"result":"pass","tested_state":"HEAD 159e178; plan/task hashes as plan2-independent-probes","output":"Fresh GET closes prior-loop cache finding; same queue ordering reaches resume selection; locked guard preserves Idle/Paused; seeded all-Done job skips network and pacing and reaches compile/ZIP producers; six defaults have correct old/new mappings; three test edits preserve assertions' purposes; gate and tool-owned register changes cover the requested work. Only batch-boundary wording needs a clerical correction.","fresh":true}
```

Executed commands were bounded `rtk proxy python -B` file reads and the scratch probe, `rtk proxy rg` source/receipt searches, `rtk proxy pwsh` completed-file reads, and `rtk proxy git status`/`git rev-parse`. Receipts preserve exits. Two exploratory reads used nonexistent infrastructure paths and were corrected; one combined read ended on a nonexistent renderer App path after returning the relevant preceding sources. None was treated as proof of absence or a product failure. No planning receipt directory was broadly enumerated.

Report parser validation: `rtk proxy python -B tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/tjr-plan2-review-round-1.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-21-transcript-job-resume/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/2026-11-21-transcript-job-resume/review2/report-state.json`, exit 0: `OK: review_mode=plan; round 1 of 3; verdict=approved; open findings=0`. This validates report structure and binding, not product execution or ledger recording.

## Verdict

**approved** — no evidence-backed High or Critical finding. The plan delivers the resume and defaults intent within the stated bodyless-route scope. Loop 1 F1 is closed. Apply the batch-boundary wording correction when carrying out DEFAULTS_CANON; it does not require another review round. Retain the stated GET-to-POST and cross-parent pacing limits without claiming stronger atomicity or a universal queue-rate guarantee.

This approves the plan, not an implementation or a successful full test run. The report is supplied at the requested temporary path for coordinator validation/copying. Completion-preflight was consulted and applied to this review artifact and unstarted task state only; no implementation row was completed by this reviewer.
