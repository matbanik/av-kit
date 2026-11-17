---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-ready-handshake/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "rh-plan-2026-11-15-ready-handshake"
round: 1
---

# Critical Review: 2026-11-15-ready-handshake

> **Review Mode**: `plan`
> **Verdict**: `approved`

## Intent Anchor

a request sent the moment `AVKIT_READY` appears is queued by a listening socket, never refused, and the desktop app's main process reads the backend's stdout as whole lines, so a ready line split across chunks, repeated, or sent beside other lines publishes the API exactly once with the right port; the ready line's text and the descriptor stay as they are.

Executing the specified changes and passing the specified rows would deliver this objective. No evidence-backed High or Critical delivery finding was identified.

## Scope

Reviewed the complete working-tree implementation-plan.md and task.md, both existing plan-local scripts, the grouping's Session 82 and ordering/decision context, the two known issues, the cited 04/06/07 contracts, CLI and main-process code, named tests, installed uvicorn/asyncio implementation, packaging spec, runtime-smoke call chain, and source helpers that row 0 will copy. Applied PR-1 through PR-9 and the Materiality Gate. Process-paperwork findings were excluded as requested.

Reviewed content identities:

| File | SHA-256 |
|---|---|
| implementation-plan.md | 34f17319305813137d2174ead2b6520779304564b00316d66d438d7ff23a49cf |
| task.md | 9927289f4b6d9eb5eb888d64276c89b7efd0d1352d1d0523666c580c0b5ad339 |
| ready-gap-probe.mjs | dbb661539163c4782f0b514a509edcacf94195a053457d93e654aa341a119697 |
| gap-tally.py | 8eb4dc0dcbabe63968064438ed88e9183eafb22fb100d0e6d2b06ae4d4d4349d |

The new product tests and both implementation handoffs are absent, and implementation rows remain unchecked. The seven existing product/test/build-plan paths checked by row 0 currently have no name-only diff against HEAD. This is a plan approval, not a claim that the implementation or packaged smoke has run.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Goal and coverage

Accepted. Every goal clause has an observable AC and a task row:

| Clause | Acceptance proof | Task rows |
|---|---|---|
| LISTEN_FIRST, dev | AC-153.1 reads SO_ACCEPTCONN at descriptor and print; AC-153.3 connects and reads health; AC-153.5 measures first-request outcomes | 2–3 |
| LISTEN_FIRST, packaged | AC-153.4 smoke; AC-153.5 first-request HTTP 200 on the freshly built scratch executable | 4 |
| READY_TEXT_KEPT | AC-153.2 pins text, flush, UUID and bound port; existing descriptor-secret/atomic-write/spawn tests run whole | 2–3, H1-2 |
| READY_LINES and correct port | AC-154.1/.2 split and mixed lines; .5 CRLF; .6 partial/invalid input; .8 real pipe | 5–6 |
| READY_ONCE and stdout ownership | AC-154.3 repeated/different-port lines, .4 no veto, .7 production hookups, .9 existing pins | 5–6 |

The production chain is explicit: CLI main → bound socket → early listen → descriptor/ready print → supplied-socket server; child stdout → onReadyOutput → one reader per boot → publishIfReady → publishBackendReady. No required goal clause is displaced into out-of-scope work.

## Q2 — Socket startup and Windows tests

Accepted D-978. Installed uvicorn is 0.54.0. Config.bind_socket binds and returns without listening (config.py:568–614). Server.run → serve → startup waits for lifespan, then passes the supplied socket and config.backlog to loop.create_server (server.py:85, :105, :115, :154). The installed Python's asyncio Server._start_serving calls sock.listen(self._backlog); create_server accepts the supplied stream socket and makes it nonblocking. There is no check that rejects an already-listening socket, and the later call uses the same backlog. The saved Windows receipt independently records bound=0, listening=1, successful relisten, backlog=2048. No new socket/network probe was run.

AC-153.1 is the decisive deterministic Red oracle: it observes the real socket before the descriptor and print, while avoiding actual server execution. The wrappers and stub are compatible with the current main(). AC-153.2 and existing descriptor tests cover preservation.

The five-spawn AC-153.3 is supplementary timing evidence, not a deterministic Red guarantee: a delayed parent can read READY after the old backend starts listening. The plan discloses this race at implementation-plan.md:174; the small sample does not establish a universal 0.2^5 bound. The 0.25 s timeout does distinguish the measured 505–524 ms Windows retry from prompt connection, and Green has no deliberate startup race after LISTEN_FIRST. S3 refuses an unproved Red rather than falsely completing it. Scheduler-induced timing failures remain possible and must be diagnosed honestly.

## Q3 — Whole lines, publication and ownership

Accepted D-977/D-979/D-980. READY_LINES waits for newline, strips one trailing carriage return, and processes mixed lines in order; READY_ONCE stops on the first successful publish and discards remaining carry. READY_BOUND specifies a bounded retained carry and poison-until-next-newline recovery, following capture-picker.ts:347–364. AC-154.5 checks recovery, AC-154.6 withholds an unterminated trailing line, and .1–.3 assert publication/query counts and the first port. This does not require Console log framing to change.

READY_NO_VETO preserves current production behavior: confirmReadyAndPublish already discards the identity comparison and publishes (python-manager.ts:110–125). The live query remains synchronous (publishIfReady:160), contrary to the plan's incidental wording about starting it with void; this does not invalidate the single-threaded latch argument. Owned stdout strengthens the current wiring, which also feeds stderr. Pre-spawn refuse/reap logic at index.ts:247–265 and shutdown ownership remain untouched. AC-108.3's query is retained and AC-154.4 explicitly pins failed-query/image-mismatch behavior. No new M-7 assertion change is needed.

The proposed handler definitions and listener order preserve AC-108.4/.6's source slices and AC-108.7's listener discovery. AC-154.7 binds the new reader to the real stdout hookup. The real-pipe test supplements synthesized chunks; 80 ms between writes is not an OS guarantee of distinct data events, and exit can precede stdio close. These are test scheduling limits, not a demonstrated missing production deliverable.

## Q4 — Measurements and scratch packaged smoke

Accepted D-981/D-983 and S7. ready-gap-probe.mjs actually issues fetch before its separate acceptance polling; cim mode runs the process query first. Independently re-running gap-tally on the saved receipts yielded 4/5 refused before, 5/5 HTTP 200 with CIM, and 10/10 HTTP 200 for the scratch fix. Its selftest passed, and --all-ok correctly rejected the before receipt with exit 1. Thus the helper checks the outcome the plan uses to gate AC-153.5.

Timing qualification: accept_after_ready_ms is a post-request connection sample, not an exact first-listen timestamp; in CIM mode it also includes the CIM and HTTP durations. The recorded CIM-only times are 440–516 ms, while 452–530 ms describes the later sample. Counts remain valid. The measurements characterize this PC and these runs.

Row 4 invokes PyInstaller directly with work/dist paths under C:/Temp/av-kit/ready-handshake/pack. The spec resolves sources through SPECPATH; it does not hard-code packaging/dist. Copying deno.exe and LICENSE.md to the scratch dist/deno matches wiring.py:124. The forbidden-folder check and runtime smoke inspect the new output; S7 forbids fallback. The smoke uses fresh temp app-data/home, dead external proxies and localhost HTTP. Its dependence on uncommitted sibling source is expressly disclosed at implementation-plan.md:456 and is acceptable for this local smoke, not a release certification.

Strict liveness is not certified: the probe gives READY a 60 s timer, but fetch/connect have no explicit per-operation deadline; the existing smoke's READY loop performs blocking readline despite its elapsed-time check (tools/smoke_packaged_tts.py:121–136). An outer watchdog would improve failure handling. These paths do not falsely pass a missing backend, and this review does not expand the session into rewriting the existing smoke utility.

## Q5 — Ordering, baselines and register overlap

Accepted. The expected uncommitted changes from Sessions 75–81 affect different product paths. The row-0 product/test HEAD checks are limited to the five files this plan edits; 04/06 permit prior Delivered notes outside the two home sections. Thus S2 does not require a clean tree or reject the grouping's expected shared-document changes. An unexpected earlier edit inside this session's implementation paths correctly triggers re-evaluation.

baseline-scope.json binds shared files to their actual row-0 bytes; baseline-dirty-hashes.json and task.md:40 preserve unrelated dirty content. S4 checks untouched scoped paths before each row and the issue-register hash before resolution. The copied identity helper binds dirty inputs and runtime versions; it may conservatively invalidate evidence when HEAD changes, which costs a rerun rather than accepting stale evidence.

MEU writes use tools/meu_status.py update/render. Issue resolution uses the existing tools/issue_triage model through the copied resolver, with the expected row-0 hash, an exclusive Windows handle and parsed-field allowlist; rendering uses issue_triage.py. It is not a hand-edited register replacement. Session 78's E2E/setup changes are read as they exist at execution; Session 83's dev-spawn.test.ts is untouched.

## Q6 — Scope, line endings and gate coverage

Accepted. Declared product/docs/register writes stay within Files Modified, the plan folder and closeout artifacts. Scratch build, probe data and smoke app-data/home stay under C:/Temp/av-kit; ordinary test/build/dependency caches and generated UI outputs are consequences of the explicitly planned suites/build/sync. No row rebuilds packaging/dist or invokes the installer. The existing packaged executable is only measured. Cleanup targets are session scratch paths, and started backend cleanup is scoped to owned process ids.

Independent byte inspection confirmed index.ts is entirely CRLF (638 LF / 638 CRLF) and test_backend_cli.py entirely CRLF (145 / 145); cli.py, python-manager.ts and test_backend_spawn.py are LF. Both Green rows and the final gate specify byte-level preservation.

The gate includes Python lint/types/tests, affected Python tests, UI types/lint/full Vitest, compiled build followed by the real Electron late-output test with ELECTRON_RUN_AS_NODE cleared, OpenAPI drift and both generated-register checks. MCP skips match the unchanged MCP source/config; the chosen Electron regression test reaches the altered output handlers. New parser behavior also has synthesized and real-pipe coverage. Scheduled baseline/checker/gate scripts are explicitly created in row 0/H1-2; their current absence is not a missing executable claim.

The latest user instruction supplies execution authorization after approval. The draft's generic instruction to await another message does not supersede it. This session still ends uncommitted with a commit-message draft.

## Checklist Results

All results concern plan readiness. Manual observer: codex-independent-reviewer; manual exit codes are null.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read both complete files; compare goal, ACs and rows 0–7/H1/H2 | null | Same two MEUs, order, changes and gate |
| PR-2 Not started | pass | Inspect plan inventory, task statuses and new-test/handoff existence | null | Four planning files; new tests and handoffs absent |
| PR-3 Task contracts | pass | Inspect task rows for owner, output, validation, dependency and status | null | Concrete commands and scheduled helper creation |
| PR-4 Validation realism | pass | Trace AC observations through current code/tests and planned commands | null | Deterministic socket oracle, parser assertions, scratch smoke; timing limits disclosed above |
| PR-5 Source backing | pass | Compare ACs/decisions to 04/06/07, issues and current ownership code | null | Sources support listen order, line reading and no veto |
| PR-6 Corrections readiness | pass | Inspect explicit two-MEU handoff/review targets | null | Round 1; no prior census required |
| PR-7 Scope discipline | pass | Compare exclusions to grouping and goal | null | No missing contracted goal behavior hidden as a deferral |
| PR-8 Controls and negative oracles | pass | Trace production callers and inspect assertion observables | null | No demonstrated material false-pass; --all-ok negative independently refused |
| PR-9 Single-statement discipline | pass | Compare named contracts, ACs and task references | null | Governing values clear; no materially ambiguous alternative |
| Tally selftest | pass | rtk proxy python -B docs/execution/plans/2026-11-15-ready-handshake/gap-tally.py --selftest | 0 | gap-tally selftest: ok |
| Before receipt tally | pass | rtk proxy python -B docs/execution/plans/2026-11-15-ready-handshake/gap-tally.py C:/Temp/av-kit/ready-handshake/gap-fetch-pre.jsonl --runs 5 --label review-dev-before | 0 | 4 ECONNREFUSED, 1 HTTP 200, no errors/problems |
| Scratch-fix receipt tally | pass | rtk proxy python -B docs/execution/plans/2026-11-15-ready-handshake/gap-tally.py C:/Temp/av-kit/ready-handshake/gap-fetch-fix.jsonl --runs 10 --all-ok --label review-scratch-after | 0 | 10 HTTP 200, no errors/problems |
| Negative tally oracle | pass | rtk proxy python -B docs/execution/plans/2026-11-15-ready-handshake/gap-tally.py C:/Temp/av-kit/ready-handshake/gap-fetch-pre.jsonl --runs 5 --all-ok --label review-negative | 1 | Expected refusal: a first request was not http 200 |
| Product execution / fresh packaged smoke | n/a | Not run under the read-only review restriction | null | No pytest, Vitest, npm, uv sync/lock, build or network requests |

```json
{"schema_version":"evidence.v1","check_id":"rh-review-source-trace","procedure":"Read both complete plan files, current CLI/main-process code and named tests, installed uvicorn 0.54.0 and asyncio socket-startup source, packaging/smoke helpers and grouping/issue contracts; inspect planned source-to-observable chains.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 82 plan readiness","phase":"plan","exit_code":null,"result":"pass","tested_state":"plan-sha256:34f17319305813137d2174ead2b6520779304564b00316d66d438d7ff23a49cf;task-sha256:9927289f4b6d9eb5eb888d64276c89b7efd0d1352d1d0523666c580c0b5ad339","output":"14 ACs cover the goal. uvicorn passes supplied socket and same backlog to asyncio; asyncio listens again. Current publisher already has no veto. Two planned tests and both MEU handoffs are absent. index.ts CRLF=638/LF=638; test_backend_cli.py CRLF=145/LF=145. No High/Critical delivery defect demonstrated.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rh-review-tally-positive","command":"rtk proxy python -B docs/execution/plans/2026-11-15-ready-handshake/gap-tally.py C:/Temp/av-kit/ready-handshake/gap-fetch-fix.jsonl --runs 10 --all-ok --label review-scratch-after","cwd":"P:/av-kit","scope":"saved planning scratch-fix receipt; not a fresh backend run","phase":"plan","exit_code":0,"result":"pass","tested_state":"gap-tally.py-sha256:8eb4dc0dcbabe63968064438ed88e9183eafb22fb100d0e6d2b06ae4d4d4349d;saved-planning-receipt","output":"runs=10; outcomes={http 200:10}; refused=0; errors=0; problems=[]","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rh-review-tally-negative","command":"rtk proxy python -B docs/execution/plans/2026-11-15-ready-handshake/gap-tally.py C:/Temp/av-kit/ready-handshake/gap-fetch-pre.jsonl --runs 5 --all-ok --label review-negative","cwd":"P:/av-kit","scope":"negative oracle against saved planning before-fix receipt","phase":"plan","exit_code":1,"result":"pass","tested_state":"gap-tally.py-sha256:8eb4dc0dcbabe63968064438ed88e9183eafb22fb100d0e6d2b06ae4d4d4349d;saved-planning-receipt","output":"Expected rejection observed: runs=5; outcomes={http 200:1,ECONNREFUSED:4}; problems=[a first request was not http 200]. Exit 1 is the successful negative-oracle observation.","fresh":true}
```

## Verdict

`approved` — the plan would deliver the registered goal. No blocking or severity-rated finding is raised. Keep the timing/liveness limitations above explicit when interpreting execution receipts; they do not establish a materially missing deliverable.

Report: C:/Temp/av-kit/rh-plan-review-round-1.md. The coordinator owns copying this complete report to the canonical path. This reviewer made no repository edits, ran no prohibited suites and made no network requests. Completion-preflight was applied to this review artifact; unstarted implementation rows were preserved under the explicit read-only assignment.

