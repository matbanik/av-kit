---
date: "2026-11-05"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s50-plan-2026-11-05-transcript-failure-reason"
round: 2
---

# Critical Review: transcript-failure-reason

> **Review Mode:** `plan`
> **Verdict:** `changes_required`

## Scope

**Intent anchor:** Session 50 makes every transcript failure or skip carry one short av-kit message. That message reaches the API, the job card, the Console and `console.log`. A YouTube block pauses the job with that message before any request is made for the next video.

**Intent achieved:** `partial`, as plan readiness. The normal blocked-job delivery path is specified, but skips, secrets and early resume have concrete gaps.

**Target:** working-tree implementation plan and task for Session 50, MEU-115 then MEU-116. **Reviewer:** Codex / OpenAI, class `avkit_independent_reviewer`; Claude Code / Anthropic authored the plan. **Checklist Applied:** PR-1–PR-9 and the materiality gate.

Observed HEAD is `097e0bbcf196fdf0896d4f2e5159be03f69aa62a`; the supplied `ed64f7e` is the plan's reference baseline. No finding is raised about historical hashes. Target-only Git status reports both plan files untracked; implementation rows are unchecked and neither implementation handoff exists. Reviewed SHA-256: implementation plan `40d29ef1370ee0bf9680361cdf5cad00a39232b5c39337bb379ee650fcfab0ee`; task `8323ed5ec59ca3902284ab0d719a0cb0ee11a46725fcc39e6f8b220ada61c046`.

Accepted as given: Mat's scope/order, D-247, the text approval gate, scheduled helper creation, token estimate, squashed history, unrelated session state and absent GUI references. All writes were under `C:/Temp/av-kit`; no product suite, session gate, network call, real YouTube client, repository mutation, commit or push ran. No forbidden secret or fleet-hub file was opened.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | Confidence: High. AC-115.10 cannot hold with the prescribed Console change. Per-field redaction sanitizes the composed message, but HealthService returns the original error/detail/video_id fields to downstream structlog processors. A probe using production _ensure_processor and the proposed formatting produced a redacted ring entry followed by a second stdout line containing the synthetic Bearer secret. Violates AC-115. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:178; packages/core/src/avkit_core/services/health.py:159 | Sanitize or remove the original structured values before downstream rendering, and make AC-115.10 inspect complete stdout through production structlog wiring. | open |
| F2 | High | yes | behavior | Confidence: High. The non-library exception rule retains unsafe text before storing it. A requests ConnectionError from the fake API containing https://example.invalid/caption?token=SYNTHETIC_API_MARKER survives the proposed first-line/200-character rule unchanged. It then reaches item.error_message, the API/card and the logs; redact_message does not recognize token= or URLs. AC-115.4 therefore admits credential-bearing reasons that AC-115.10's kept-field fixtures do not cover. Violates AC-115. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:143; docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:158; packages/core/src/avkit_core/services/health.py:33 | Define a safe reason policy for unexpected errors before persistence and truncation; remove URL credentials/query secrets and redact credential text. Test the adapter-to-item-to-API and complete logging paths with synthetic secrets. | open |
| F3 | High | yes | behavior | Confidence: High. A one-video job with no captions ends Done with a Skipped item. The API can return last_item_message, but the renderer displays it only while Processing and explicitly leaves Done unchanged (AC-115.14), so the finished card still gives no reason. Its sole WARNING skip event also never reaches console.log with log_to_file off. This misses the registered goal and D-218's requirement that Skipped receive the same treatment. Violates AC-115. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:157; docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:180; docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:194 | Render a latest skip reason on completed cards, including items with no title, and persist transcript skip outcomes with the toggle off. Add a single-video skip delivery test covering API, card, Console and console.log. | open |
| F4 | High | yes | behavior | Confidence: High. The new automatic pause publishes Paused inside _run_parent while the worker is still alive. If Resume arrives there, resume_processing sets the job Processing and _pick_processing=True without starting another worker. The existing worker then unconditionally resets _pick_processing=False at line 373, ignores that Processing job in _next_job, and becomes Idle. A deterministic probe reproduced job=Processing, runtime=Idle. AC-116.2's ordinary post-exit resume does not cover this interleaving. Violates AC-116. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:208; packages/core/src/avkit_core/services/transcript.py:373; packages/core/src/avkit_core/services/transcript.py:234 | Coordinate automatic pause publication, worker exit and resume so an accepted resume cannot lose its work-selection state. Add a barrier-controlled test that resumes before _run_parent returns and proves the pending videos finish. | open |
| F5 | High | yes | behavior | Confidence: High. The no-extra-wait default contract conflicts with counting retries. With defaults and one first-video retry followed by success, attempt 301 starts at 3324 seconds under existing pacing: 299*6 + 5*300 + 30. Enforcing 300 attempts/hour requires a 276-second cap wait. AC-116.5 cannot simultaneously promise no additional wait for that default run and preserve D-220's retry-inclusive cap; a retry-free 400-video run misses this conflict. Violates AC-116. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:216; docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:223; docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:306 | Limit the unchanged-pacing guarantee to the retry-free case. Add a default-settings retry case that expects the necessary cap wait and independently asserts no more than 300 starts in any rolling hour. | open |

## Checklist Results

### Information Retrieval (IR)

Observer for manual observations: `codex-independent-reviewer`; exit code `null`.

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| Target and readiness | pass | Read plan/task; target-only Git status; check implementation handoff existence | null | Both target files are untracked, rows unchecked, handoffs absent. |
| Canon and boundaries | pass | Read residual spec; look up issue IDs and D-218/D-219/D-220/D-234; compare source labels and port callers | null | MEU sequence and rider agree; only service consumes the port result in production. |
| Plan-time register receipt | pass | Read `C:/Temp/av-kit/s50/probe-issue-decisions.txt` | null | Failed-reason has D-218/D-234; block-stop has D-219/D-220; rider has no decision log; absent issue is refused. |

### Design Review (DR): Q1–Q8

**Q1 — Delivery: partly accepted; F1–F3 block.** The prescribed real HealthService automatically installs its processor; wiring constructs it at `wiring.py:205`. TranscriptService's production logger therefore reaches it without an extra subscription. Calling the actual `_job_out(service, service.get_job(id))` exercises the route's formatter and item query; using a fabricated output DTO would not. AC-116.7 plus the route and renderer tests can prove the ordinary blocked case with the toggle off; require actual service logging, not a direct call to `_process`. Failed parent messages are populated; the all-skipped/final-skipped Done case remains hidden (F3). AC-116.7 alone does not cover that or secret-bearing errors.

**Q2 — Port/adapter: mapping accepted, unsafe fallback rejected (F2).** Installed 1.2.4 confirms 429 → IpBlocked at `_transcripts.py:95`, with IpBlocked a RequestBlocked subclass. The named reason classes exist; NotTranslatable/TranslationLanguageNotAvailable and other CouldNotRetrieveTranscript subclasses can safely use a class-name fallback. Cookie classes are outside that superclass but their cookie-auth paths are disabled in this installed version. Requests transport/JSON/XML exceptions can still take the generic fallback. Preserve NoTranscriptFound's inner `continue` and the any-language listing fallback; it means no preferred-language match, whereas TranscriptsDisabled means no caption tracks. Only exhaust the fallback into a skip. The service is the sole production port caller; FakeCaptions and adapter tests require migration. MCP passes route JSON through. The illustrative port signature at `01-domain-layer.md:447` still says None and should follow the new type (nonblocking documentation note).

**Q3 — Console: partly accepted; F1/F2 block.** Redact-then-cap avoids cutting a recognized needle before detection. Per-field single-line normalization and the whole-message pass protect the composed message, not the original downstream fields. The probe confirms two stdout lines and a secret in the second. PERSIST_LEVELS, exception/fatal/warn aliases, a dedicated append lock, catching OSError around the entire directory/open/write operation, and a thread-local recursion guard are sound designs. A broad catch or logging recursively from the OSError handler would be inappropriate; neither is prescribed. Existing HealthService test constructors inspected use tmp_path. Transcript/settings/console Electron launches set AVKIT_APP_DATA to fresh temp directories, and main honors it at `index.ts:148`; no real-log write path was found in those launches. The compare helper is a useful guard, not prevention.

**Q4 — Block stop: partly accepted; F4 blocks.** Pending with retry_count zero, a fixed reason and a global pause before the next job are faithful to D-219. Resume clears the parent reason and Done clears the item reason. A reasonless pause preserves any existing reason; it does not itself guarantee an empty one, but normal initial/manual pause has none. Existing stop handling cancels Processing/Paused jobs at the worker boundary. The newly proposed pause inside _run_parent introduces the demonstrated resume interleaving with the worker's unconditional selection-flag reset; test resume before worker exit. AC-11.6's new outcome is faithful, and changing AC-11.8's cause to DomainError preserves its Failed-parent/no-ZIP purpose.

**Q5 — Rate cap: retry-free boundary accepted; F5 blocks the broader claim.** With no retry, start k is `6*k + 300*floor(k/50)`: start 301 is 3600 and the rolling maximum is 300 when the left boundary is excluded. One default retry changes that result to 3324 and 301 starts/hour without cap waiting. A retry-free 400-video run catches the exact-hour boundary but cannot validate the retry claim. The described one-second wait slices, settings reread, empty-deque exemption for fractional caps, and cap-zero escape can work without deadlock; add deterministic in-wait pause/stop, raised-cap and zero-cap cases to distinguish them. The plan counts port attempts, including retries, consistently with its fake-port test scope; it does not instrument individual HTTP subrequests inside a library fetch.

**Q6 — API/renderer: mostly accepted; F3 blocks skip presentation.** Reuse exactly the item chosen by _aggregates (maximum non-null processed_at, otherwise final listed item) for title/status/message; do not independently select the last nonempty error. Pending blocked items use the parent's reason. The OpenAPI addition is isolated in principle; regeneration has not run and no resulting diff is certified. TR5's planned amendment permits job-message; layout-canon checks mockup inventories, not live component ids. Adding a help topic preserves AC-23.16's minimum-topic guard. Settings tests pin the path and row controls; retaining those suffices (they do not actually pin the full “Persist to” prefix). Existing transcript E2E uses null error messages in its ordinary Done/Processing fixtures, so those expectations can remain. Open folder is available for Failed and Paused whenever output_dir is nonempty (`transcript-controls.ts:82`, menu at `transcript-card.ts:112`).

**Q7 — Red/guards: feasible with the delivery corrections; no additional false-passing task predicate demonstrated.** Hasattr/signature assertions allow required missing-name tests to fail by assertion rather than setup error. AC-115.12 explicitly catches OSError; AC-115.10 combines its field and secret assertions; guards AC-116.3/5 are intentionally not required in Red. The copied checker requires each requested failure and uses a digit boundary, so 115.1 does not stand in for 115.10. The row-1 skip fixture is not selected until row-2 Green, when the type and service branch exist; moving its import into the body prevents collection failure. Row-2's broad `ac_11_` selection runs existing transcript tests as intended; row-3 and row-8 expressions select their named families in the supplied files. No product collection or runner was invoked. When writing row-8 Reds, explicitly migrate the temporary exhausted-block subcases of AC-115.5/7 as well as AC-11.6: §Service already says MEU-116 replaces that outcome, while row-9 runs all these tests. Keep non-block expectations immutable. F1 and F5 currently make their stated Green contracts incompatible with the prescribed behavior; they are product/test-contract failures, not a demonstrated gate bypass.

**Q8 — Order/safety: accepted.** Fake ports and patched adapter factories avoid YouTube; MCP audit is correctly skipped. Tests' app-data isolation plus the real-log comparison are appropriate. Row 10's proposed copy retains Session 49b's writer-denying Windows handle from read through replacement, compares the expected hash under that handle, stages and validates serialization, and restricts parsed changes to the three named issues' allowed keys. S3 alone does not serialize writes, but the handle does: another writer is refused instead of overwritten. No register writer ran during review. Skipping MCP build with no source change, live audit with no YouTube authorization, and installer build-record with no installer build is justified; MCP type/tests and OpenAPI still run. Commit drafting does not authorize a commit. No task row independently authorizes an outward action.

### Plan Review (PR)

| Check | Result | Manual procedure/evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compared rows, work packages and scope; same MEU order and delivery paths. |
| PR-2 Not started | pass | Target-only status and handoff checks described above. |
| PR-3 Task contract | pass | Read rows: roles, outputs, exact commands, dependencies and statuses are specified. |
| PR-4 Validation realism | fail | F1, F3 and F5 expose missing/incompatible outcome assertions. |
| PR-5 Source-backed planning | pass | Compared FIC with Mat's brief, targeted issue decisions and residual sections. |
| PR-6 Corrections readiness | pass | Handoff/review targets named; first round has no correction census due. |
| PR-7 Scope discipline | pass | Checked exclusions against brief/residuals; deferred MEU-122 is the named Session 53 dependency. |
| PR-8 Reachability/negative oracles | fail | F1/F2/F4 are concrete downstream/state failures; additional task-predicate false pass not demonstrated. |
| PR-9 Single statement | pass | Named contracts govern the reused sets; F5 identifies a substantive rate-contract conflict separately. |

Adversarial role checks: AV-1/AV-3 are plan feasibility only, not implementation Red/Green certification; AV-2/AV-4 have no prescribed assertion bypass or skip masking; AV-5 implementation placeholders are not applicable to this unstarted plan; AV-6 source labels were checked. No Critical finding.

### Executed evidence

The probe uses production HealthService wiring with only the proposed field formatting substituted in memory, a patched fake caption API, pacing arithmetic from the existing loops, and a deterministic pause/resume interleaving through the actual worker/resume/selector. It does not claim the future implementation has been executed.

```json
{"schema_version":"evidence.v1","check_id":"s50-plan-adversarial-probes","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s50-review-probes.py","cwd":"P:/av-kit","scope":"planned field formatting, generic error reason, default request timing and automatic-pause/resume boundary","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"working-tree plan SHA256 40d29ef1370ee0bf9680361cdf5cad00a39232b5c39337bb379ee650fcfab0ee; task SHA256 8323ed5ec59ca3902284ab0d719a0cb0ee11a46725fcc39e6f8b220ada61c046; production methods plus explicitly described in-memory substitutions","output":"ring contains synthetic marker: False; complete stdout contains synthetic marker: True; stdout lines: 2; planned item/API message retains https://example.invalid/caption?token=SYNTHETIC_API_MARKER; no-retry request301=3600 rolling maximum=300; one-retry request301=3324 rolling maximum=301 required cap wait=276; immediate resume: job=Processing runtime=Idle pick_processing=False","fresh":true}
```

Other executed commands: `rtk proxy git --no-optional-locks rev-parse HEAD` (exit 0, hash above); target-only `git status --porcelain --untracked-files=all -- docs/execution/plans/2026-11-05-transcript-failure-reason` through rtk proxy (exit 0, two untracked files; Git emitted global-ignore permission warnings); bounded Python -B reads/hashes and targeted rg sweeps. An initial child-PowerShell read failed with “Missing variable name after foreach”; it was replaced with successful Python reads. One rg sweep named a nonexistent generic fixtures.ts and exited 2; actual launch functions were then read from each named Electron spec. Neither failure was treated as verification evidence.

## Verdict

`changes_required` — five High behavior findings prevent readiness against the registered intent. Correct F1–F5 in the plan and test contracts, then resubmit the same loop. No repository correction was made. Residual limits: no product tests, OpenAPI regeneration, gate execution or network behavior was run; helper safety and future test feasibility are assessed from their described behavior and current source. User-facing wording remains Mat's decision.

Output preflight: `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s50-review-output-check.py`, exit 0: `PASS: repository v2 JSON schema; report metadata; five findings; Q1-Q8; PR-1-PR-9; citations; unchanged target hashes`. Completion-preflight was consulted for this review artifact; the implementation task intentionally remains unstarted under the user's read-only boundary.

Report saved only at `C:/Temp/av-kit/s50-plan-review-round-1.md`; the coordinator owns canonical publication.


## Recheck (2026-11-05)

**Round:** 2. **Agent:** `codex-independent-reviewer`, OpenAI/Codex, independent of the Anthropic/Claude Code author. **Workflow:** `/plan-critical-review`. **Current verdict:** `approved`. **Current open findings:** 0.

**Intent anchor:** Session 50 makes every transcript failure or skip carry one short av-kit message. That message reaches the API, the job card, the Console and `console.log`. A YouTube block pauses the job with that message before any request is made for the next video.

**Intent achieved:** `yes`, as plan readiness. This does not certify implementation or authorize execution through the human gate. Round 1 above is preserved as history; this section gives the current disposition.

Reviewed working-tree SHA-256: plan `f3991470b17409d54afd24a4ec6e81c40acfe683379fc99967dd9cb47a2e4363`; task `ef8b66303099d976dee0d808aa1a029370f39cce64f7b3e3b64633908d23f81a`. Observed HEAD: `097e0bbcf196fdf0896d4f2e5159be03f69aa62a`. Implementation rows remain unchecked and both implementation handoffs are absent. Only temporary files were written. No pytest, Vitest, Playwright, session gate, network request, real YouTube client, repository mutation, commit or push ran. Forbidden secret files and fleet-hub paths were not opened.

### Prior Pass Summary

| Finding | Prior Status | Recheck result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |
| F3 | open | fixed |
| F4 | open | fixed |
| F5 | open | fixed |

### Findings

Severity below records the original finding; all five are now fixed and nonblocking. No new High or Critical failure was demonstrated.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | no | behavior | Fixed: the downstream mapping drops raw fields and disables traceback output; AC-115.10 inspects complete stdout through production structlog wiring. The corrected in-memory delta removed the demonstrated secret from stdout, ring and file. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:195; :287; task.md:46 | Retain the complete-output assertions. See the nonblocking stdout clarification below. | fixed |
| F2 | High | no | behavior | Fixed: non-library errors yield only their class name; DomainError text is redacted before SAFE_REASON strips URLs and caps it. AC-115.19 covers the adapter and domain paths through persistence/API/logging. The original synthetic URL-secret counterexample no longer survives the modeled rule. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:126; :158; :173; :296 | Implement the specified ordering and keep both end-to-end negative cases. | fixed |
| F3 | High | no | behavior | Fixed: a completed skip fills SKIPPED_JOB_MESSAGE, Done cards show job-message, and the WARNING carries persist=True. AC-115.18 joins real service, HealthService, route formatting and file persistence; AC-115.14 covers the matching Done card. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:172; :178; :209; :295 | Preserve the one-video skip test and toggle-off persistence. | fixed |
| F4 | High | no | behavior | Fixed: selection consumes _pick_processing before _run_parent; the unconditional later reset goes; exit publication and start/resume use the same lock. AC-116.8 covers both specified pre-exit windows. A plain-Lock model using production start/resume/pause methods reached Done/Idle in both windows without recursive acquisition. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:227; :230; :335; task.md:52 | Keep lock ownership explicit and the timeout assertions. Future implementation still needs the real AC-116.8 run. | fixed |
| F5 | High | no | behavior | Fixed: the no-wait guarantee now excludes retries. AC-116.9 expects the first necessary wait and independently counts rolling starts. The model produced 0 extra seconds without retries and 276 seconds with one first-video retry, maximum 300 starts per open-left hour. | docs/execution/plans/2026-11-05-transcript-failure-reason/implementation-plan.md:243; :244; :336 | Preserve both default runs and the independent rolling-window oracle. | fixed |

### Nonblocking clarification

AC-115.10's final clause at `implementation-plan.md:287` says stdout has no lines besides those `_process` prints. Section Console at `:195` also retains a downstream renderer. Applying that prescribed delta to the production chain produced 14 safe stdout lines for seven events: the JSON line and the sanitized downstream rendering. The concrete F1 credential leak is closed. Align the test's line-count clause with that stated design by checking every emitted line for unsafe fields/tracebacks; a requirement for exactly one emitter would need an explicit design choice. This inherited duplicate rendering does not prevent the registered delivery intent and is not a new blocker. The Settings tests likewise pin `logs/console.log` and row controls, not the literal “Persist to” prefix; retaining the prefix remains compatible.

### Q1–Q8

**Q1 — Delivery: accepted.** AC-116.7 uses real TranscriptService and HealthService, whose constructor installs `_dispatch` ahead of the configured structlog chain (`health.py:96-111`; application construction at `packages/api/src/avkit_api/wiring.py:205`). The actual `_job_out(service, service.get_job(id))` exercises the same formatter as GET (`routes/transcripts.py:35`, `:138`); fabricated DTOs or directly calling `_process` would not satisfy this contract. The route and renderer tests cover the remaining boundaries. Failed parents gain JOB_MESSAGE; Done skips now gain SKIPPED_JOB_MESSAGE, card coverage and file delivery. No remaining planned silent Failed/Skipped card path was demonstrated. Legacy pre-session stored messages are not migration evidence.

**Q2 — Port and adapter: accepted.** Installed 1.2.4 confirms 429 → IpBlocked (`_transcripts.py:95-96`) and the relevant exception classes. Preserve NoTranscriptFound's inner `continue`, then the any-language listing fallback: no preferred-language match is not proof that captions are disabled. Only exhausted/empty listing becomes no_captions; VideoUnavailable remains distinct. Fixed library reasons/class-name fallback avoid library paragraphs, and generic transport text is discarded before item persistence. DomainError text follows redact → URL replacement → cap. Only the transcript service consumes the port in production; FakeCaptions and adapter tests migrate, and MCP passes route JSON through. The old illustrative None signature in `01-domain-layer.md:447` remains a documentation follow-through note, not a missing production caller.

**Q3 — Console: accepted, with the stdout clarification above.** PERSIST_LEVELS and aliases preserve ERROR/CRITICAL persistence; PERSIST_FIELD adds just the skip WARNING. Per-field single-line → URL removal → redaction → cap prevents the demonstrated cut/needle and URL leaks; the whole-message redaction remains a final pass. Returning only safe event/seq/false exc_info closes the demonstrated downstream leak, including exception text in tracebacks. Catch OSError around the complete mkdir/open/write operation, use a separate append lock, and never recursively log from its failure handler. Thread-local re-entry correctly distinguishes recursion from another logging thread. Inspected tests use tmp_path and the three scoped Electron launchers use fresh AVKIT_APP_DATA; main honors it (`index.ts:148`). The real-log comparison detects an accidental write but does not itself prevent one. Existing file format/location remain compatible with Settings and packaging text updates.

**Q4 — Block stop: accepted as a feasible contract.** Pending with retry_count zero, a reason on parent/item and global pause before selecting another job match D-219. Resume clears the parent reason and completes pending items; DomainError still fails only its video. D-306 removes the concrete lost-selection/reset and live-thread-exit windows. `_next_job` owns its selection lock; exit paths own their critical sections; the plan explicitly forbids reacquiring the plain Lock inside either. The model exercised production start/resume and the existing pause helpers without nested acquisition. Stop retains precedence at the worker boundary; start still selects Pending rather than silently resuming Paused jobs. No new material start/pause/stop race was demonstrated. AC-11.6's amendment follows block stop; AC-11.8's DomainError fixture preserves its Failed-parent/no-ZIP purpose.

**Q5 — Rate cap: accepted.** The retry-free formula places request 301 at 3600 seconds; evicting entries at or before the left boundary permits it without extra wait. A 400-video run crosses that boundary. An inclusive-left mutation was rejected by the temporary oracle. One retry moves the uncapped request-301 start to 3324; the required 276-second wait now has its own AC and independent maximum-starts check. Count port calls, retries included, consistently with the fake-port brief; this does not claim to count every HTTP subrequest inside one library fetch. Slice models exercised stop, pause, cap raised and cap zero within one second, and fractional caps emptied the deque without deadlock. Real implementation timing is still untested.

**Q6 — API and renderer: accepted.** Message/title/status must use the same item chosen by `_aggregates`: maximum non-null processed_at, otherwise the last listed item (`routes/transcripts.py:29-32`). Do not independently choose the last nonempty error. Pending blocks use the parent message. OpenAPI regeneration is planned and bounded to last_item_message; no generated diff is certified yet. TR5 is expressly amended, while layout-canon reads the mockup inventory. The help change adds a topic and retains AC-23.16's required topics. Existing ordinary Done/Processing E2E fixtures remain compatible. Open folder is available on Failed and Paused when output_dir is nonempty (`transcript-controls.ts:82-83`; `transcript-card.ts:112-113`).

**Q7 — Red and guards: accepted as feasible, subject to the minor stdout clause correction.** New-name tests first assert hasattr/signature, required OSError tests catch and assert rather than fail by exception, and AC-116.8's timeouts fail by assertion. The copied checker accepts an assertion fixture and refuses child exit 0; its exact-title match refuses 115.10 as evidence for 115.1. Row 1's skip import stays inside the body, so it does not break collection; row 2 introduces the type and changes the service branch before selecting AC-11.6. Its broad ac_11_ selector currently reaches 15 existing functions, rather than an empty set. New families are introduced in their own Red rows; row 8 selects the temporary AC-115.5/7 block-subcase migrations, AC-11.6/8 and all AC-116 tests. Guards 116.3/5 intentionally pass and are not required Red failures. No additional materially false-passing task/gate predicate was demonstrated; no runner or collection was invoked.

**Q8 — Order and safety: accepted.** The task retains Mat's execution gate and uses fake ports/patched adapter factories. E2E app-data isolation and the real-log guard are specified. Row 10's multi-issue writer must retain Session 49b's handle that denies writers/replacement, compare the expected SHA under that handle, validate a staged serialization, and allow parsed differences only in the three named issues' permitted keys (`register-rewrite.py:167-209`, `:340-398`; plan `:454`). S3 protects session scope; the handle/hash protect the read/write interval. No register writer was run. MCP types/tests and OpenAPI remain gates; skipping unchanged MCP build, live network audit and an absent installer build-record is justified. No row authorizes commit/push or a YouTube request. D-304/305 options truthfully describe their scope and tradeoffs; their choice and the message texts remain Mat's at the gate.

### Checklist Results

All manual observations below: observer `codex-independent-reviewer`, exit `null`. “Pass” assesses plan feasibility, not execution results. Process-paperwork conditions outside Mat's review scope were not used to manufacture blockers.

| Check | Result | Procedure / evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Re-read both corrected files; rows 3/4/8/9 and H1-7/H2-2 cover amended ACs and decisions in dependency order. |
| PR-2 Not started | pass | Unchecked implementation rows, absent handoffs and unchanged product signatures/OpenAPI observed. |
| PR-3 Task contract | pass | Inspected owners, deliverables, commands and dependencies for scoped implementation/verification rows. |
| PR-4 Validation realism | pass | Outcome tests cover the five corrected failures; note the nonblocking stdout clause clarification. |
| PR-5 Source-backed planning | pass | Compared Mat's brief, residual spec and targeted D-218/D-219/D-220/D-234 register entries; D-247 accepted as given. |
| PR-6 Correction readiness | pass | Stable handoff/review targets and F1–F5 corrections are actionable; no process-paperwork refusal applied. |
| PR-7 Scope discipline | pass | Required delivery retained; upstream block remains open; MEU-122 is the named downstream session. |
| PR-8 Reachability/negative oracles | pass | Traced real HealthService wiring and route formatter; repeated original failures and modeled corrected deltas; no new material control defeat demonstrated. |
| PR-9 Single statement | pass | SAFE_REASON, persistence and rate contracts are named; retry/no-retry distinction resolves the material contradiction. |

AV-1/AV-3 assess prospective Red/Green and assertion feasibility only. AV-2/AV-4: no prescribed test bypass or masking. AV-5: implementation placeholders not applicable to an unstarted plan. AV-6: source-backed behavior checked. No Critical finding.

### Executed evidence

The original probe was rerun unchanged: it still reproduces the original unsafe stdout, URL leak, request timing and lost-resume behavior. That is the unchanged product baseline, not a failure of the corrected plan. The second probe applies explicitly identified source substitutions in memory for the Console/adapter rules, models the deque cap and D-306 worker ownership, and retains production start/resume/pause helpers. It establishes feasibility and closes the original counterexamples; it does not execute future code or count as AC test evidence.

```json
{"schema_version":"evidence.v1","check_id":"s50-r2-original-counterexamples","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s50-review-probes.py","cwd":"P:/av-kit","scope":"repeat round-1 counterexamples on unchanged product baseline","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"HEAD 097e0bbcf196fdf0896d4f2e5159be03f69aa62a; original round-1 in-memory substitutions","output":"ring marker False; complete stdout marker True; URL query marker retained under old rule; no-retry request301=3600 peak=300; one-retry request301=3324 peak=301 required wait=276; immediate resume job=Processing runtime=Idle pick_processing=False","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s50-r2-corrected-plan-model","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s50-r2-probes.py","cwd":"P:/av-kit","scope":"corrected Console and generic adapter deltas, safe domain reason, skip persistence, rate and worker-lock feasibility","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"plan SHA256 f3991470b17409d54afd24a4ec6e81c40acfe683379fc99967dd9cb47a2e4363; task SHA256 ef8b66303099d976dee0d808aa1a029370f39cce64f7b3e3b64633908d23f81a; explicit in-memory substitutions/models","output":"youtube-transcript-api 1.2.4; synthetic secrets absent from ring/stdout/file; traceback suppressed; 14 sanitized stdout lines for 7 events; skip WARNING persisted with toggle off; ordinary WARNING/INFO absent; adapter reason ConnectionError; domain reason GET [link] [REDACTED]; wrong-boundary mutation rejected; no-retry extra wait=0; one-retry extra wait=276; both peaks=300; inside-parent and sleep-zero resume models Done/Idle peak workers=1 without plain-Lock deadlock; target hashes unchanged","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s50-r2-guard-model","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s50-r2-guard-probes.py","cwd":"P:/av-kit","scope":"copied Red-check functions, targeted selectors, rate slice model, unstarted-state inspection","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"corrected plan/task hashes above; current Session 49b checker and service test source","output":"assertion fixture accepted; exit-0 fixture refused; 115.1 does not match 115.10; row-2 ac_11_ selects 15 existing functions; cap=2 expires at 3600; fractional=.5 empties at 3601; stop/pause/raise/off handled in one slice; implementation handoffs absent and rows unchecked; last_item_message absent in baseline OpenAPI","fresh":true}
```

Read-only source sweeps and bounded reads supplied the manual observations. One initial child-PowerShell command failed on variable interpolation and one search named a nonexistent guessed wiring path; successful Python reads and a corrected path sweep replaced them. Neither failed command is counted as verification. No product suites, regeneration or future helper execution are claimed.

### Verdict

`approved` — F1–F5 are fixed in the plan, with zero current blocking findings. Executing the corrected contracts is capable of delivering the registered intent. Align the minor AC-115.10 stdout clause with its retained sanitized renderer; do not treat duplicate safe baseline rendering as the original secret leak. D-304/D-305 choices and user-facing text approval remain Mat's. Residual limits: real implementation, full gate, generated OpenAPI diff and real concurrency behavior await execution and independent execution review.

The completion-preflight skill was consulted for review-output checks only; its implementation checklist does not authorize performing the untouched task. Report saved only at `C:/Temp/av-kit/s50-plan-review-round-2.md`; the coordinator owns canonical publication.

Output preflight: `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s50-r2-output-check.py`, exit 0: `PASS: v2 schema and negative fixture; unchanged round-1 body; round-2 approved with 0 open findings; F1-F5 dispositions; Q1-Q8; verbatim intent; unchanged plan/task hashes`. The repository review-state parser also exited 0: `review_mode=plan; round 2 of 3; verdict=approved; open findings=0`.
