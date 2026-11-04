---
date: "2026-10-16"
project: "2026-10-14-backend-robustness"
meus: ["MEU-76", "MEU-78", "MEU-77"]
plan_source: "docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-16 Meta-Reflection

> **Date**: 2026-10-16
> **MEU(s) Completed**: MEU-76 (api-error-surface), MEU-78 (svc-ffmpeg-resolver), MEU-77 (svc-tts-async-generate)
> **Plan Source**: docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   The authoritative gates. `-Check windows-gate` ran four times (A-12: the gitignored region-picker stub was never built in this worktree; then the first run of record; then the rerun after execution R1 F1; then the rerun after the A-14 plan rewording), and `-Check audit` ran five times (A-11 cleared its own live receipt; the A-10 follow-through moved the fingerprint; then the R1 F1 rerun and the A-14 rerun). Each run takes 20 to 40 minutes. The plan review also took four rounds: the cancel/shutdown concurrency (plan F1, F2) needed D-25, D-30 and D-31 before the reviewer could find no more interleavings.

2. **What instructions were ambiguous?**
   Two plan contracts did not match the code. AC-78.4 named a `gpu_capabilities()` cache that does not exist (A-8), and AC-78.9 said to type into an input that is `readOnly` (A-9). `PARTIAL_CLEANUP`'s root did not say whether it meant the root at write time or at cleanup time; the execution review found the second reading was a defect (R1 F1).

3. **What instructions were unnecessary?**
   The handoffs restate project-wide gate evidence (fingerprints, suite counts) that `walkthrough.md` holds canonically, so every gate rerun forced three handoff edits plus a walkthrough record. A pointer to the walkthrough record would carry the same information.

4. **What was missing?**
   Row 0's install list does not build gitignored test prerequisites (`native/**/publish/`), so a fresh worktree fails the Electron capture-picker tests (A-12). The row 1 census missed a third closed `MediaPort` method list (A-10). The handoff template's YAML Decision Log was not checked until H2-1; the handoffs were written as prose and had to be converted (D-43). A structure check at H1-7 would have caught it then.

5. **What did you do that wasn't in the prompt?**
   Re-observed the MCP `runner-fake-backend` flake five times in isolation and once as a full suite before accepting A-13, rather than retrying the gate. Converted the handoff Decision Logs to YAML (D-43). Cited every A-decision in the Decisions Log, not only the plan and grouping rows the validator requires.

### Quality Signal Log

6. **Which tests caught real bugs?**
   `test_ac_77_5_cleanup_uses_job_paths_after_output_path_changed` (R1 F1): all four cases failed Red on the round-1 code, leaving the old-root WAV and MP3 behind. The threaded AC-77.9 (e) to (h) barrier tests forced the reservation and caller-drain designs (D-30, D-31) to be exact. The census itself caught three fakes that would have returned 500 or doubled counts (A-5 to A-7).

7. **Which tests were trivially obvious?**
   The AC-76 `GUI_ERROR_TEXT` negative cases (a 422 keeps its message) restate an unchanged branch; they guard against a regression, not a defect.

8. **Did pyright/ruff catch anything meaningful?**
   No defects. pyright kept the `partials` tuple typing honest during the F1 correction; ruff was clean throughout.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   Yes for MEU-76 and MEU-77; the named contracts (`CANCEL_RULE`, `SHUTDOWN_STOP`, `AUDIT_CANCEL_STEP`) mapped one-to-one to tests. MEU-78's FIC needed two human corrections (A-8, A-9) because it described code the planner had not read.

10. **Was the handoff template right-sized?**
    Mostly. The AC table and FAIL_TO_PASS rows were useful to the reviewer. The final-evidence paragraph duplicates the walkthrough (see Friction 3).

11. **How many tool calls did this session take?**
    Not tracked precisely; several hundred across planning, execution and closeout, with two context compactions.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    None. Every row was correctness-class or gate work held by the coordinator (Claude Code, Opus 5.5). The plan and execution reviews went to Codex `gpt-6.1-sol` at high effort through `tools/Invoke-CodexDispatch.ps1`; that is review, not delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | grouping | When are the gated build-plan edits (matrix rows, MEU-79's 11 section, 06/gui-actions-index) written? | autonomous | After Session 30's execution review approves; the grouping writes only ungated homes and the SSOT | Local Canon | Carried from grouping §8 D-1. Session 30's windows-gate-check refuses any GATED_PATHS change after its gate, so editing them early would reopen it. Session 33 touched none of those homes. | — |
| D-2 | grouping | Does MCP-SETUP-PROMPT join Session 31? | human | Yes, as MEU-71; Session 31 becomes P3 | Human-approved | Carried from grouping §8 D-2. It shares SettingsPage.tsx and the Settings Electron wave with MEU-70. No effect on Session 33's scope. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-3 | grouping | Are the tech-debt rows MEUs? | autonomous | No; a separate debt batch | Local Canon | Carried from grouping §8 D-3 (issue-triage.md TECH-DEBT rule). Session 33 kept MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT out of scope accordingly. | — |
| D-4 | grouping | Session order | autonomous | 31 → P2 sessions 32, 33, 34 → P3 35, 36 → P4 37, 38, 39 | Local Canon | Carried from grouping §8 D-4. Session 33 ran in its own worktree beside Session 31 (plan D-10), which the order allowed. | — |
| D-5 | grouping | Keep TTS page work (MEU-75, MEU-79) out of the engine session? | autonomous | Yes, Session 35 after Session 33 | Local Canon | Carried from grouping §8 D-5. MEU-77 changed only the generate contract the TTS page consumes; the page work stays in Session 35. | — |
| D-6 | grouping | Where does the independent MEU scoping review run? | human | Codex scoping review on the grouping draft, not during triage | Human-approved | Carried from grouping §8 D-6. Its status was still 'not yet run' at planning; plan D-9 records why this plan's own review covered the scope. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-7 | grouping | Repair the shared status_labels in meu-status.yaml? | autonomous | Yes: every row's labels rebuilt from its own status | Local Canon | Carried from grouping §8 D-7. H2-2 renders and checks the registry after the MEU-76/77/78 status change. | — |
| D-8 | planning | Where do the gates run, given the driver is local Claude Code on Windows? | autonomous | Everything local: one validate-task.ps1, no .sh, no container pre-gate; the driver runs WINDOWS_GATE and the authoritative MCP audit | Local Canon | The grouping's container/local split assumed a cloud driver. Here the driver is on the target machine, so a container rehearsal adds a round trip and no evidence. The authoritative gate runs on the same Windows host either way. Precedents: .agent/context/harness.local.md §Claude Code (local driver, pwsh, rtk); grouping :107 — the MCP audit re-baseline and WINDOWS_GATE are local stages; docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.ps1 — the audit and gate checks this plan reuses. | — |
| D-9 | planning | Is the grouping's §9 scoping review (not yet run) a prerequisite for this plan? | autonomous | No; this plan's own independent review covers the three MEUs' scope | Local Canon | §9's criteria (traceability, one coherent change per MEU, dependencies) are checkable on this plan; the plan review receives the grouping as canon. Waiting would block every P2 session on an unrelated registry problem. Precedents: .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md:231 — status 'not yet run', fallback reviewer Mat; docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md — Session 30 executed with the same §9 review pending. | — |
| D-10 | planning | How is the overlap with Session 31 (executing in P:/av-kit) handled? | autonomous | Work in the separate worktree; row 0 records the overlapping paths; whichever session merges second resolves; S4 stops on a real conflict | Local Canon | The shared files are edited in different regions (Session 31: section frames and rail; Session 33: the Dependencies card and a new spec). A rebase now would pull unreviewed Session 31 code into this gate. Precedents: git -C P:/av-kit log -1 — 0cfa40a, Session 31 R1 fixes on claude/vigilant-volta-f04tvs; Session 31 plan Files Modified — SettingsPage.tsx, ui/tests/e2e/settings.test.ts. | — |
| D-11 | planning | Split MEU-77 to Session 33b? | autonomous | Not up front; split at row 8 only if context passes about 50 % (S9) | Local Canon | The three MEUs share one OpenAPI diff, one audit and one gate. Splitting up front doubles the gate cost; S9 keeps the escape. Precedents: grouping :109 — split flag 'candidate'; Session 30 execution — one plan carried REST+MCP+audit work. | — |
| D-12 | planning | Dispatch the plan review to Codex without asking first? | autonomous | Yes, with a metered-dispatch warning before each dispatch | Local Canon | The workflow mandates the dispatch; the warning keeps the cost visible. Precedents: .agent/workflows/create-plan.md §5 — auto-dispatch with a correction loop; PROFILE B2 — metered reviewer. | — |
| D-13 | planning | Which event and fields carry the unhandled-error log? | autonomous | ERROR_EVENT: api.unhandled_error with request_id, route, method, error, exc_info; mapped statuses are not logged | Spec | The spec asks for request id, route and traceback. Mapped 503s are expected states (ffmpeg missing, capture unsupported) that already have their own messages; logging them as unhandled would bury real faults. Precedents: docs/build-plan/04-rest-api.md:433; packages/core/src/avkit_core/services/tts.py — tts.generate_failed (event + job_id + error) pattern; packages/core/src/avkit_core/services/health.py:37 — CONSOLE_FIELDS. | — |
| D-14 | planning | How does the 500 get CORS headers? | autonomous | Catch in the existing request_id_middleware, which already runs inside CORSMiddleware | Research-backed | No new middleware and no ordering change. Re-ordering CORS or a second CORS layer would affect every response; catching where the request id is already bound also gives the log its id. Precedents: packages/api/src/avkit_api/main.py:73-90 — middleware order; docs/build-plan/04-rest-api.md:431 — local probe on Starlette 1.6.0. | — |
| D-15 | planning | Which status does a yt-dlp extract failure map to? | autonomous | ExtractError -> 422 with yt-dlp's message | Spec | The URL was well-formed but YouTube refused it; the user must act (cookies, another URL). 422 matches AgeRestrictedError, the closest existing case. 502 was rejected: av-kit is not a gateway, and a 5xx would be masked. Precedents: docs/build-plan/04-rest-api.md §Status mapping — 422 for a request that cannot be processed as given (AgeRestrictedError, CookieTestError are 422); packages/api/src/avkit_api/errors.py:25-38. | — |
| D-16 | planning | Cache the ffmpeg resolution at all? | autonomous | No cache: resolve on every use (a few stat calls); only GPU capabilities stay cached, per path | Spec | A cache needs an invalidation signal from settings; resolving costs less than one ffmpeg spawn. GPU capability probing spawns ffmpeg, so it keeps a cache keyed by the binary. Precedents: docs/build-plan/03-service-layer.md:492 — 'a missing binary is not latched'; docs/build-plan/02-infrastructure.md:430 — 'Probe binary once; cache' (superseded). | — |
| D-17 | planning | Does cancel remove partial output, against 05:95 'files already written stay'? | autonomous | Yes: remove the job's .wav and .mp3 on Cancelled and Failed; correct 05:95 | Spec | 03:477 is the later, MEU-specific rule (Triage D-44). Under synchronous generation 05:95 was moot because nothing could cancel a running job. Precedents: docs/build-plan/03-service-layer.md:475 — 'no partial output file remains'; packages/core/src/avkit_core/services/capture.py:900 — _unlink_if_file. | — |
| D-18 | planning | Which status does generate return, given the spec says Queued/Running? | autonomous | Generating (the TTS enum's running state); Pending is never returned | Local Canon | Generic queue words in 03:476; TTS runs one job, so the job is running from the moment it is accepted. Returning Generating keeps the GUI's polling unchanged. Precedents: packages/core/src/avkit_core/domain/tts.py:35-36 — Pending -> Generating -> Done/Failed/Cancelled; ui/src/renderer/src/features/tts/useTtsJob.ts:64 — polling keys on Generating. | — |
| D-19 | planning | What happens to the 03:423 rule that an unexpected exception is re-raised (500)? | autonomous | The worker records Failed with the exception type and message ('Type: message'), logs with exc_info and never re-raises; amend 03:423 | Spec | There is no request left to fail once generate has returned. The message rule (every Failed job carries one) is kept; only the re-raise is gone. TA-7, TA-8 and TA-9 follow from this. Precedents: docs/build-plan/03-service-layer.md:422; docs/build-plan/03-service-layer.md:474 — synthesis runs in the background. | — |
| D-20 | planning | Guard model unload while a job is generating? | autonomous | Out of scope; the adapter's existing errors mark the job Failed | Local Canon | WORKER_RULE turns that error into a Failed job with a message. A new 409 on unload is a separate contract change. Precedents: packages/infrastructure/src/avkit_infra/tts/adapter.py:263-264 — 'no model is loaded' raises ModelLoadError. | — |
| D-21 | planning | Change the MCP client timeout? | autonomous | No; client.ts is unchanged | Local Canon | Generate now returns in milliseconds, so the timeout no longer bites. The grouping lists client.ts as a candidate file only. Precedents: mcp-server/src/client.ts:14 — 30 s. | — |
| D-22 | planning | Does the TTS run bar need a GUI change? | autonomous | No code change; AC-77.14 is a pin (RED_RULE item 5) over the existing polling and cancel | Local Canon | The run bar already polls a Generating job (W2-4) and cancels (W2-5) against the seam, which answers Generating. Under a synchronous backend it never saw one in production. The Electron suite runs on renderer fetch seams, so it cannot observe the backend; the backend contract is AC-77.10. AC-77.14 pins the GUI half so a later GUI change cannot drop it. Precedents: ui/src/renderer/src/features/tts/useTtsJob.ts:64-78 — refetchInterval while Generating; ui/src/renderer/src/features/tts/tts-controls.ts:23-24 — Generating blocks generate and enables cancel. | — |
| D-23 | planning | Where are the H2-2 known issues resolved? | autonomous | H2-2 resolves API-UNHANDLED-ERROR-OPAQUE, FFMPEG-RESOLUTION-DIVERGENCE and MCP-TTS-GENERATE-SYNCHRONOUS with evidence files under the plan directory | Local Canon | Same closeout path as Session 30. Precedents: docs/execution/plans/2026-10-02-capture-flatten-backup/task.md H2-2; .agent/context/known-issues.yaml:1102,1181,1892. | — |
| D-24 | planning | What does generate return: the in-memory job or the stored row? | autonomous | get_status(id): the row as stored, after the worker was spawned | Local Canon | With a synchronous test spawn the row may already be Done; returning the stored row keeps the REST answer truthful in both modes. Precedents: packages/core/src/avkit_core/services/tts.py:103-108 — get_status. | — |
| D-25 | planning | How are cancel and the worker's terminal write ordered (plan review R1 F1)? | autonomous | _lock is the single linearization point: cancel sets the flag under it only for the current job; _finish reads the flag, writes the terminal row and clears _current_id and the flag in one critical section | Local Canon | With only unlocked flag checks, a cancel between the last check and the Done write leaves a Done row while the route answers 204, and its flag can cancel the next job. One lock around the decision and the write makes each cancel either fully before (Cancelled, no output) or fully after (no-op). Precedents: packages/core/src/avkit_core/services/tts.py — _lock already guards the 409 check and _current_id. | — |
| D-26 | planning | What happens at shutdown when the TTS worker does not stop within the timeout (R1 F2)? | autonomous | stop_processing returns the wait result; the lifespan skips models.unload and the engine dispose when it is False; _closing refuses new generate calls | Local Canon | Tearing the model and database down under a live worker turns a slow stop into a crash path. Skipping both is safe because the process is exiting; the daemon thread dies with it and the next start fails the row. Precedents: packages/api/src/avkit_api/main.py:39-50 — _lifespan; TTSService.recover_stale_processing — RESTART_RECOVERY. | — |
| D-27 | planning | How does the audit's tts.cancel step avoid racing a job that finishes first (R1 F3)? | autonomous | destructiveStep gains optional raceLost and attempts; tts.cancel retries up to 3 times only when its job turned Done before the confirmed call | Local Canon | A long text makes the race unlikely but not impossible on a fast machine. Retrying only on Done keeps a real failure (still Generating, or Failed) a failure, and the default of one attempt leaves every other step unchanged. Precedents: mcp-server/scripts/audit/plan.ts:206-265 — destructiveStep precondition and reestablish. | — |
| D-28 | planning | What does a rerun of the audit compare against (R1 F5)? | autonomous | The pre-session baseline from baseline.sha, written over the baseline file before every attempt; failure restores the start-of-check copy and deletes the attempt's plan-folder evidence | Local Canon | After one passing attempt the baseline already holds tts.cancel pass, so a rerun would report UNCHANGED and AUDIT_EXPECT would refuse. Comparing every attempt with the committed pre-session file keeps FIXED reproducible. Precedents: mcp-server/scripts/audit/classify.ts — computeDelta (pass→pass is UNCHANGED); mcp-server/scripts/audit/run.ts — --baseline is the comparison and the update target. | — |
| D-29 | planning | Which paths do GATE_FINGERPRINT and AUDIT_FINGERPRINT bind (R1 F4, F6)? | autonomous | The whole working tree minus GATE_EXCLUDED (the files rows after the gate write); the audit fingerprint is measured before the prep and after the carry | Local Canon | An include-list misses gate inputs (other plan dirs, workflows, schemas, templates). Excluding only the files later rows write binds everything else, and the post-review rerun covers the tests that read the excluded files. Precedents: docs/execution/plans/2026-09-26-framework-update-adoption/adoption-manifest.json — gate tests read files far outside the code dirs; .agent/workflows/mcp-audit.md — read by the audit. | — |
| D-30 | planning | How does shutdown see a TTS job that was admitted but whose worker has not started (R2 F2)? | autonomous | _current_id is the reservation, published under _lock at admission and cleared only by _finish; wait_idle waits on a Condition over _lock until it is None; the worker checks the flag before prepare | Local Canon | Waiting on a thread misses the interval between admission and spawn. The reservation already exists and is cleared on every path (worker finally and spawn failure), so waiting on it makes accepted work busy until its terminal write. Spawn stays outside the lock because a synchronous spawn re-enters _lock in _finish. Precedents: packages/core/src/avkit_core/services/tts.py:89,160-166 — _lock (threading.Lock) already guards _current_id at admission; TTSService._finish — CANCEL_RULE (D-25). | — |
| D-31 | planning | How does shutdown see a generate caller that still touches a collaborator after the reservation clears, or before admission (R3 F2)? | autonomous | generate enters under _lock (refused when _closing, before any collaborator call) and increments _callers; a finally decrements it under _idle and notifies; wait_idle waits until _current_id is None and _callers == 0 | Local Canon | The reservation covers the worker but not the caller: a fast or synchronous worker clears it before the caller's get_status read, and the synchronous checks call the model port before admission. Counting each call from entry to return covers both without holding the non-reentrant _lock across spawn and keeps the stored-row return (D-24) for a synchronous spawn. Precedents: packages/core/src/avkit_core/services/tts.py:103-108 — get_status opens a unit of work; packages/core/src/avkit_core/services/tts.py:131-139 — get_model_status, list_voices and _require_assets run before admission; D-24 — generate returns the stored row after spawn. | — |
| D-32 | execution | Where does _route get the include prefix? | autonomous | From the public route path_regex | Local Canon | MEU-76 handoff Decision Log. The private effective-route context key can change between FastAPI versions; path_regex is public. | — |
| D-33 | execution | Does GUI_ERROR_TEXT also apply to a masked 503? | autonomous | Yes; the contract keys on the internal_error code | Local Canon | MEU-76 handoff Decision Log. Keying on the status would treat two internal_error responses differently. | — |
| D-34 | execution | Does configured_source read settings on every resolution? | autonomous | Yes, one single-row read per call, nothing cached | Local Canon | MEU-78 handoff Decision Log. RESOLVER_ORDER requires the live value; a cache would reintroduce the divergence the MEU removes. | — |
| D-35 | execution | Is yt-dlp's ffmpeg_location set when ffmpeg came from PATH? | autonomous | Yes, always the resolved directory | Local Canon | MEU-78 handoff Decision Log. Same directory yt-dlp would search; one code path; the ffprobe sibling rule still matches. | — |
| D-36 | execution | How do the AC-77.10 POSTs avoid racing the 5 s worker gate? | autonomous | A non-waiting _post_generate; _generate adds wait_idle | Local Canon | MEU-77 handoff Decision Log, FIXTURE_REPAIRS (f). No assertion or request body changed. | — |
| D-37 | execution | Which log events cover unnamed failure paths? | autonomous | tts.finish_failed and tts.cleanup_failed | Local Canon | MEU-77 handoff Decision Log. Keeps the worker's never-raise contract with a trace; silent on a normal run. | — |
| D-38 | execution | Does _finish hold _lock across the terminal write? | autonomous | Yes, the D-25 barrier as one critical section | Local Canon | MEU-77 handoff Decision Log. A racing cancel then finds no current job, so its flag cannot leak into the next run. | — |
| D-39 | execution | When does an audit step's detail get the attempt prefix? | autonomous | Only when attempts > 1 | Local Canon | MEU-77 handoff Decision Log. Every other destructive step's detail stays byte-identical for baseline carry and AUDIT_EXPECT. | — |
| D-40 | execution | How does reestablish recreate the tts.cancel precondition? | autonomous | REST POST /tts/generate; anything but 201 is precondition_lost | Local Canon | MEU-77 handoff Decision Log. A lost precondition must not read as a cancel that passed against nothing. | — |
| D-41 | execution | Execution review R1 F1: which paths does Cancelled or Failed cleanup unlink? | autonomous | The WAV and MP3 paths _work captured before the write | Local Canon | MEU-77 handoff Decision Log and plan §Execution Correction Notes. Re-reading tts.output_path at cleanup cannot be made correct after a mid-job settings change. | — |
| D-42 | execution | Is the on_progress flag read locked? | autonomous | No; _finish re-reads it under _lock | Local Canon | MEU-77 handoff Decision Log. The read is an early-exit hint; the decision is the locked re-read (D-38). | — |
| A-1 | execution | S4: the branch moved from 7861020 to c72fc44 after planning; three Files Modified paths changed upstream | human | Accept c72fc44 as the planning head; no rebase | Human-approved | walkthrough §Gate decisions A-1. The DEPS_CARD lines were byte-identical after the shift; only cites moved. | USER_EXPLICIT 2026-10-15 'Accept c72fc44 (Recommended)' |
| A-2 | execution | headroom.exe appeared on PATH and the prereq guard refused | human | not_applicable for the execution phase | Human-approved | walkthrough A-2. No approved Headroom disposition, no MCP connection, and the payloads are exact evidence. | USER_EXPLICIT 2026-10-15 'not_applicable (Recommended)' |
| A-3 | execution | prereq-plan-review used --cap 3 but the approved plan review is round 4 | human | --cap 6 | Human-approved | walkthrough A-3. The ledger was untouched; only the stale caller cap changed. | USER_EXPLICIT 2026-10-15 'set cap to 6' |
| A-4 | execution | prereq-uv-sync failed: uv picked CPython 3.14 and spacy has no cp314 wheel | autonomous | Recreate .venv with CPython 3.12.12, the main checkout's interpreter | Local Canon | walkthrough A-4. Environment only; no gate, test or plan change, so the obviousness test passed. | — |
| A-5 | execution | Census N-1: two probe tests pass only with ffprobe on PATH | human | FIXTURE_REPAIRS (g): sibling fake ffprobe.exe | Human-approved | walkthrough A-5. Fixture only; no assertion change. | USER_EXPLICIT 2026-10-15 'Sibling ffprobe.exe (Recommended)' |
| A-6 | execution | Census N-2: SimpleNamespace dependencies() fakes would raise under DEPS_FFMPEG | human | Add ffmpeg_path=None, ffprobe_available=False to those fakes | Human-approved | walkthrough A-6. Corrects repair (d); no assertion change. | USER_EXPLICIT 2026-10-15 'Add the fields to fakes (Recommended)' |
| A-7 | execution | Census N-3: one shared _Spy would double the shutdown counts | human | A separate no-op tts fake in _services() | Human-approved | walkthrough A-7. Extends repair (e); no assertion change. | USER_EXPLICIT 2026-10-15 'Separate tts no-op fake (Recommended)' |
| A-8 | execution | AC-78.4 names a gpu_capabilities() cache that does not exist | human | Retarget AC-78.4 to detect_gpu() | Human-approved | walkthrough A-8 and MEU-78 handoff Decision Log. Inventing a cache would add unscoped behavior. | USER_EXPLICIT 2026-10-15 'Retarget to detect_gpu (Recommended)' |
| A-9 | execution | The FFmpeg path input is readOnly; how does AC-78.9 write ffmpeg_path? | human | Drive it through browse-ffmpeg-btn | Human-approved | walkthrough A-9 and MEU-78 handoff Decision Log. Browse is the only writing control; UX unchanged. | USER_EXPLICIT 2026-10-15 'Use Browse (Recommended)' |
| A-10 | execution | A third closed MediaPort method list broke under ffmpeg_binaries | human | TA-11: add ffmpeg_binaries to the keep tuple | Human-approved | walkthrough A-10 and MEU-78 handoff Decision Log. An explicit TA keeps the test change reviewable. | USER_EXPLICIT 2026-10-15 'Add TA-11 (Recommended)' |
| A-11 | execution | -Check audit cleared its own live receipt with -Filter s33-audit* | human | Skip the live receipt in the cleanup; rerun H1-2 | Human-approved | walkthrough A-11. The cleanup deletes strictly less; no evidence touched. | USER_EXPLICIT 2026-10-15 'Skip the live receipt (Recommended)' |
| A-12 | execution | H1-3 ui-electron failed: the gitignored region-picker stub was never built in this worktree | human | Build the stub, rerun H1-3 from the start | Human-approved | walkthrough A-12. Environment gap; no tracked or fingerprinted path changed. | USER_EXPLICIT 2026-10-16 'Build stub, rerun gate (Recommended)' |
| A-13 | execution | gate77 rerun after R1 F1: 2 of 423 MCP runner-fake-backend tests failed with a runner error | autonomous | Re-observe without edits; H1-3 is the gate of record; a repeat stops for Mat | Local Canon | walkthrough A-13. The file never reaches tts.py; 5/5 isolated runs 9/9 and the full suite 423/423. Same obviousness class as A-4. | — |
| A-14 | execution | The closeout validator's PLACEHOLDER regex read literal brace and angle-bracket text in plan D-17 and D-19 as unfilled template markers | human | Reword both chosen texts with the same meaning; rerun H1-2 and H1-3 from the start | Human-approved | walkthrough A-14. The plan is fingerprinted, so the reword invalidated the audit and gate; rerunning before review round 2 keeps the reviewed tree final. | USER_EXPLICIT 2026-10-16 'Reword now, rerun (Recommended)' |
| D-43 | closeout | The three handoffs' ## Decision Log sections were prose bullets, which the closeout validator refuses | autonomous | Rewrite each bullet one-for-one as a canonical decision_log YAML entry (D-32 to D-42; A-8 to A-10 keep their IDs) | Local Canon | The handoff template and human-decision-protocol §6 name the fenced YAML as the only form; no bullet was dropped or added, and the handoffs are GATE_EXCLUDED. IDs continue after D-31 so none collides with a planning-stage entry. | — |

Triage decisions behind the three resolved issues (`API-UNHANDLED-ERROR-OPAQUE`, `FFMPEG-RESOLUTION-DIVERGENCE`, `MCP-TTS-GENERATE-SYNCHRONOUS`) are cited in prose only: they live in each issue's `enrichment` and were consumed through the grouping, not re-decided here.

---

## Pattern Extraction

### Patterns to KEEP
1. Red before every correction, including the review-driven one: the R1 F1 regression failed in all four cases before `tts.py` changed.
2. One A-row per gate failure, with the receipt, the classification and the decision, before any rerun (A-4, A-10 to A-13).
3. Fingerprints measured before and after the audit (plan F4), so a late edit visibly invalidates the evidence instead of silently relabelling it.

### Patterns to DROP
1. Restating gate counts and fingerprints in each handoff; point to the walkthrough record instead.

### Patterns to ADD
1. A row-0 step that builds gitignored test prerequisites (the region-picker stub) in a fresh worktree.
2. Run `--handoff-structure-only` at H1-7 so the handoff Decision Log form is checked before closeout.
3. When a contract names a path or root, state when it is captured (write time or use time).

### Calibration Adjustment
- Estimated time: one execution day after a one-day plan.
- Actual time: planning 2026-10-14 to 2026-10-15 (four review rounds); execution and closeout 2026-10-15 to 2026-10-16.
- Adjusted estimate for similar MEUs: budget two authoritative gate runs and one review correction for any threaded-service MEU.

---

## Next Session Design Rules

```
RULE-1: Every contract that names a filesystem root or setting says when it is read (captured once, or read at use).
SOURCE: execution review R1 F1 (PARTIAL_CLEANUP's root re-read at cleanup).
EXAMPLE: "unlink the job WAV under the output root" → "unlink the WAV path the job built before its write".
```

```
RULE-2: Row 0 builds every gitignored artifact the authoritative gate's tests spawn.
SOURCE: A-12 (capture-picker tests spawned a stub the worktree never built).
EXAMPLE: install list ends at `npm ci` → install list also runs `npm --prefix ui run build:picker-stub`.
```

```
RULE-3: The census sweeps every closed list of a port's members, not only the fakes.
SOURCE: A-10 (test_ac_28_7's keep tuple was the third closed MediaPort list).
EXAMPLE: grep fakes for the new method → also grep `__dict__`, `dir(` and literal method-name tuples.
```

---

## Next Day Outline

1. Target MEU(s): Session 34 per the 2026-10-09 grouping (D-4 order).
2. Scaffold changes needed: add the picker-stub build to the plan template's row 0 install list.
3. Patterns to bake in from today: RULE-1 to RULE-3; capture-time wording for any path contract.
4. Codex validation scope: plan review at high effort, cap 6, as here.
5. Time estimate: one planning day and one execution day.
6. Merge order: whichever of this worktree and any concurrent session merges second resolves overlap (plan D-10).

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not tracked precisely (several hundred) |
| Time to first green test | MEU-76 Green on 2026-10-15, right after its Red receipts |
| Tests added | pytest: 12 new test functions in existing files and 48 in four new files (suite 724); MCP Vitest 411 → 423 (+12 in three new files); ui Vitest +2 new-file cases plus appended api-fetch cases (suite 804); Electron suite 139; one existing expectation amended under TA-11 (A-10), the others by approved TA-1 to TA-10 |
| Codex findings | Plan review: R1 changes_required (4 High, 2 Medium, 2 Low), R2 changes_required (1 High), R3 changes_required (1 High), R4 approved. Execution review: R1 changes_required (1 High: cleanup re-read `tts.output_path`), R2 approved (0) |
| Handoff Score (X/7) | 6/7 (the MEU-77 handoff's cleanup claim missed the mid-job settings change until R1 F1) |
| Rule Adherence (%) | 90 |
| Prompt→commit time | 2026-10-14 → not committed (Mat commits) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes, including the R1 F1 correction |
| No test expectation change without approval | AGENTS.md §Testing & TDD | Yes. TA-1 to TA-10 were plan-approved; TA-11 and the fixture repairs A-5 to A-7 were ruled by Mat before they were applied |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex `gpt-6.1-sol` wrote every verdict; reports were spliced verbatim |
| A gate failure gets an A-decision, never a silent fix | cloud-local §3.5 | Yes (A-4, A-10 to A-13) |
| Handoff Decision Log in the template's YAML form | human-decision-protocol.md §6 | **No until H2-1.** Written as prose and converted at closeout (D-43) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-33-backend-robustness-2026-10-16"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 2}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: windows_shell_powershell, cited: true, influence: 2}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: rtk_token_optimized_commands, cited: true, influence: 1}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, execution_session, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: [quality_gate]
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md
    - docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md
    - docs/execution/plans/2026-10-14-backend-robustness/task.md
    - docs/execution/plans/2026-10-14-backend-robustness/walkthrough.md
    - docs/execution/reflections/2026-10-10-gui-polish-residuals-reflection.md
decisive_rules:
  - P1:tests-before-production-corrections
  - P1:human-approval-for-test-changes
  - P1:independent-review-no-self-approval
  - P1:gate-failure-preserve-classify-decide
  - P1:no-tolerated-failure-in-authoritative-gate
conflicts:
  - "The system reminder asks for a Co-Authored-By trailer on commits; the user's standing rule forbids AI attribution trailers, and the user's rule wins."
  - "The zero-tolerance authoritative gate met a non-reproducible MCP runner flake in a targeted gate (A-13); the gate of record (H1-3) had to be the arbiter instead of a retry."
note: "Session 33 ships logged CORS-safe 500s and the typed extract error (MEU-76), one live ffmpeg resolver (MEU-78) and async, cancellable TTS generate (MEU-77); the MCP audit passes 99/99 with tts.cancel FIXED."
slim_candidate: ["Handoff final-evidence paragraphs duplicate walkthrough gate records; a pointer would do", "The handoff Decision Log YAML is checked only at closeout; moving the check to H1-7 would remove a late rewrite"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 4, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 4, medium: 2, low: 2}
    - {review: plan, round: 2, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 4, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 1, medium: 0, low: 0}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 1
  finding_categories: {behavior: 7, contract_drift: 1, other: 3}
  verdicts: {changes_required: 4, approved: 2}
meu_work_classes: [correctness, mixed, correctness]
```
