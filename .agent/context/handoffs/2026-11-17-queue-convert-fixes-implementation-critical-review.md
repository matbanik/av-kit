---
date: "2026-11-17"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-17-queue-convert-fixes/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "qc-execution-2026-11-17-queue-convert-fixes"
round: 1
---

# Critical Review: 2026-11-17-queue-convert-fixes

> **Review Mode:** execution
> **Verdict:** approved

## Scope

Session 89, MEU-156 and MEU-157. Codex independently reviewed the Anthropic-authored implementation against AC-156.1 to AC-156.13 and AC-157.1 to AC-157.14, within the delta from baseline `9d6d172778763fdf61ba3af165dea0243a1e6f9f`. Reviewed the plan/task, both handoffs, five product deltas, all eight changed/new test files, supporting callers, plan-local scripts and baseline records, substantive document/register deltas, and saved Red/Green/Electron/gate receipts. Applied relevant IR and AV checks. Approved decisions D-1100 and D-1105 to D-1111 are the boundary; D-1112 to D-1114 were checked for soundness.

**Intent anchor:** on the Convert and Downloader pages Cancel is disabled while the queue is Paused, and the toolbar's card Cancel, the palette's "Cancel conversions" and "Cancel downloads" and the cancel confirm all follow that one rule; Cancel stays enabled while a job runs, `Pausing…` included; one Ctrl+O on Convert opens exactly one file picker whether it is pressed before or after the lazy Convert page mounts; no service, API route, OpenAPI document or MCP tool changes; Electron E2E tests on the real backend prove both, with no network and no manual check.

**Intent achieved:** yes. No Critical or High finding, regression, or required correction established. Reviewer writes are confined to `C:/Temp/av-kit`; the coordinator publishes the report and completes H2.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal

Accepted every clause within the approved renderer-cache boundary. The toolbar itself has Start, Pause/Resume, Clear finished and More; Cancel is the running card action, as the plan's actual wiring describes. No separate toolbar Cancel was added or left enabled.

| Goal clause | Implementation and AC proof |
|---|---|
| Cancel unavailable while Paused on both pages | Processing-only rules at `convert-controls.ts:87` and `download-controls.ts:78`; command guards, PAGE_STATE and confirm gates. AC-156.1 to AC-156.10 assert rules, requests, cards, palette state and confirm lifecycle; AC-156.11/.12 exercise Electron. |
| Cancel remains available during Processing, including Pausing… | The rules depend on processor state, not the pending-pause mark. AC-156.1 to AC-156.5/.8/.11/.12 cover running/restored Cancel; unchanged AC-155 tests and the pause-feedback Electron suite cover Cancel during Pausing…. |
| Exactly one picker before or after lazy mount | Press-time token at `convert-commands.ts:355`, delivery at `:368`, take at `:394`, acknowledgement/mount effect at `ConvertPage.tsx:508`. AC-157.1 to AC-157.11/.14 cover token delivery, dropping, StrictMode and actual Electron IPC counts; AC-157.12/.13 preserve repeats and pins. |
| Services/API/OpenAPI/MCP kept | Independent comparison confirms all 355 baseline skip files unchanged, no additions/removals, and no OpenAPI document delta. SERVICES_KEPT and TRANSCRIPT_STOP_KEPT hold. |
| Automated Electron proof without external network/manual check | FFmpeg-generated local media and real Convert backend; controlled Downloader fetch seam after real-backend launch; file-protocol delay and counting IPC picker in Electron. Saved runs and gate pass at the current identity. |

No unproved in-scope goal clause found. Downloader's seam is renderer proof on an app with a real backend, as approved; it does not claim a real YouTube download.

## Q2 — Cancel paths

Accepted CANCEL_WHEN_RUNNING, CANCEL_PALETTE, CANCEL_CARD and CANCEL_GUARD. PAGE_STATE reads the common rule (`ConvertPage.tsx:584`, `DownloaderPage.tsx:556`); palette filtering requires published true state (`shortcuts.ts:267`). Neither cancel command has a keyboard chord. Direct card callbacks call `cancelConversion`/`cancelDownload`, whose existing guards refuse a cached Paused envelope (`convert-commands.ts:285`, `download-commands.ts:210`). `QueueList.tsx:215` marks only `current_job_id` in flight, and `QueueCard.tsx:353` offers Cancel only there. Both services report no current job while Paused.

CONFIRM_CANCEL_GATE reads the latest render's ctxRef (`ConvertPage.tsx:247,269`; `DownloaderPage.tsx:261,309`), including a request delivered after navigation from another page. A delayed event either meets a mounted page's current rule or has no listener; it cannot open an actionable Paused cancel. CONFIRM_CANCEL_CLOSE checks `confirm?.kind === 'cancel'` and `!cancelEnabled` (`ConvertPage.tsx:283`, `DownloaderPage.tsx:323`), so clear/remove/bulk-remove confirms remain unaffected. `[confirm, cancelEnabled]` includes the values it uses; ctxRef need not resubscribe. The saved lint step passes with zero warnings. Confirm callbacks still pass through the same command guard.

Accepted the disclosed CANCEL_STALE_POLL residual. A renderer still showing Processing may POST during one stale poll, but cancellation merely sets the service flag (`conversion.py:277`, `download.py:456`). Start clears it (`conversion.py:259`, `download.py:438`), and Resume calls Start, so that stale flag does not cancel the resumed job. This approval does not claim a fresh backend-state check on every click.

SERVICES_KEPT and TRANSCRIPT_STOP_KEPT hold. Transcript's unchanged stop rule includes Paused (`transcript-controls.ts:68`); `transcript.py:275` immediately applies Stop without an active worker and `:739` cancels paused jobs. No additional live Paused cancel route or unintended confirm closure found.

## Q3 — Browse hold

Accepted BROWSE_HOLD, BROWSE_DROP, BROWSE_ACK and BROWSE_TAKE_ON_MOUNT. The token is created synchronously on the first press. A second waiting/held press schedules nothing. Mount takes either a waiting or held token, removes the drop listener, and opens the picker once. The old deferred run compares token identity and therefore becomes inert after a take, drop or replacement. StrictMode's second effect setup finds no request. A delivered cancelable event is acknowledged synchronously before browseForFiles, and clearBrowseRequest removes the drop listener on acknowledgement, off-route delivery, explicit take and hashchange drop.

Navigation uses `navigateShell` (`shell-nav.ts:4`), which changes the hash before synchronously dispatching hashchange. The new listener is installed before navigation, so a cross-page browse request sees `/convert` and survives; leaving via the same helper drops it immediately. The listener also handles native hashchange. No stale request or accumulating listener was established for these paths.

AC-157.5 really controls frame batches (`convert-browse-hold.test.ts:102`); callbacks scheduled within a frame wait for the next frame. AC-157.14 uses the real page inside StrictMode and covers both requested histories (`convert-page.behavior.test.ts:835`): mount after the first run, and mount between its two frames; a subsequent completed-request press opens its own picker. AC-157.6 also unmounts and mounts again after consumption. These are meaningful assertions, rather than a uniform-delay claim about frame placement.

The independent Node probe of copied token logic passed 70 histories: 64 placements of two pre-mount presses and frames with StrictMode-style cleanup/setup, four leave-and-return cases spanning waiting/held requests, mounted repeated deliveries and a cross-page request. One hundred acknowledged presses left zero drop listeners. Native EventTarget/CustomEvent checks confirmed dispatchEvent returns false after preventDefault on a cancelable event, with a noncancelable negative control. This bounded probe supplements the saved real React/Electron tests; it is not a new React suite run. No duplicate or stale picker was found. CHORDS_CHECKED holds; F1 remains the separately registered gap.

## Q4 — Electron proofs

Accepted the approved delay/proof design. `convert-browse-mount.test.ts:172` delays the matching ConvertPage file chunk by 1,500 ms before serving its original response. The retained row-3a probe uses the same match/delay/fetch mechanism and measured `delayed=1`, `absentAt200ms=true`, `mountedMs=1683`, `mounted=true`, `errors=[]`. The race tests throw a setup error if the page is already present at their precondition; the two-press test additionally checks absence after both presses. The old-product Electron Red failed AC-157.8/.9 with expected 1, received 0, supporting that this fixture exposed the intended race.

AC-157.11 waits two frames and another 150 ms after the chord, then requires the page still absent before leaving (`:255`). This reaches the held-request drop path instead of merely abandoning delivery before its frames run. The strict frame-straddle proof remains in units, not the 1,500 ms delay.

Convert's two local 89-second re-encode Cuts provide real worker state transitions. AC-156.11 asserts Paused/Done/Pending and, after Resume and card Cancel, Idle/Done/Cancelled; natural completion cannot satisfy that final result. Downloader's seam reports a null current job while Paused, counts cancel POSTs and handles Resume without a network download. PAUSED_FIXTURE is confined to the new unit cases, with the existing shared fixtures unchanged. Both new Electron launchers use scratch AVKIT_APP_DATA, retain their Electron child handle and record backend pid/start time; cleanup targets only those identities. The gate's recorded backend pid 68120 cleanup follows that check. The reviewer started no application or backend process.

| Independently recounted saved evidence | Result |
|---|---|
| Race spec, four titles repeated 20 times | AC-157.8: 20; AC-157.9: 20; AC-157.10: 20; AC-157.11: 20; 80 passed |
| AC977_KEPT repeat | AC-97.7: 20; 20 passed |
| Three Cancel-while-Paused runs | 2 passed (33.7s); 2 passed (34.8s); 2 passed (38.9s) |
| Surrounding row-5 suites | Convert: 23 passed; Downloader: 26 passed; pause-feedback: 4 passed |
| Fresh gate Electron suites | Cancel: 2; browse: 4; Convert: 23; Downloader: 26; pause-feedback: 4 passed |

D-1112 is a test-helper synchronization fix: CommandPalette's open effect resets query before its timer focuses input (`CommandPalette.tsx:89`), so waiting for focus before fill prevents the helper racing that reset. It changes no product code or assertion. The earlier failed run remains disclosed. D-1114's `^ +ok +[0-9]+ ` correctly accepts padded list-reporter run numbers. The independent recount additionally required unique sequential result numbers, E2E file paths, exact AC boundaries and duration suffixes; all 100 repeat lines were actual passing results, with no failed/flaky/skipped outcome. No unrelated line inflated the observed counts.

S8 holds for this work: the handler mechanism matches the successful feasibility probe, the runner configuration has one worker and no retries, and the evidence shows no raised timeout or delay-handler repair used to obtain the pass. No new Electron correctness failure established.

## Q5 — Red, Green, pins and gate

Accepted PINS_NAMED. The existing-test diff changes only `convert-page.test.ts:429` and `downloader-page.test.ts:293`, both Paused-cancel true to false. Both page behavior files otherwise contain insertions only. The full `convert-queue.test.ts`, including AC-97.7's body, matches its row-0 hash. No existing assertion outside the named pins was edited, removed or weakened; S5 holds in the delivered delta and saved Green/full results.

Independent red-check executions accepted all 10 required MEU-156 unit failures, all eight required MEU-157 unit failures, and both required Electron failures, with their nonzero child exits. They are assertion failures: Paused cancel true/POST/modal, missing takeHeldBrowse asserted as undefined, missing held picker, and Electron picker count 0 instead of 1. No setup/import/launch failure is substituted for the Red. Green receipts show 216 and 148 passes. Every current Red-bound test hash matches; for the shared Convert behavior file, removing only the later MEU-157 inserted block exactly restores its MEU-156 Red hash. The final file also exactly matches the MEU-157 Red hash.

The gate has 24 zero-exit steps, each with its own nonempty receipt, and ends `session-gate: all steps exit 0`. Static checks, targeted sets (219/148), full UI (140 files, 1,614 tests), build, all five scoped Electron suites and both renders are present. No baseline failure was excused. Its before/after identities equal the current independently computed identity. Python/OpenAPI/MCP skips are justified by unchanged content, independently checked over all 355 skip files; unrelated Electron suites are outside the approved affected scope. The disclosed Red reruns and D-1112/D-1113/D-1114 repairs do not weaken the delivered checks.

| Test file audited (IR-5) | Grade | Basis |
|---|---|---|
| `queue-cancel-paused.test.tsx` | Strong | Exact state tables, other-control values, zero Paused requests and one running POST on both queues |
| `convert-browse-hold.test.ts` | Strong | Consumption, acknowledgement, drop and frame-controlled coalescence with exact counts |
| `convert-page.behavior.test.ts` additions | Strong | Real page command publication, modal lifecycle, kept clear confirm, real StrictMode picker counts and both frame histories |
| `downloader-page.behavior.test.ts` additions | Strong | Both directions of command/card state and cancel-versus-clear modal behavior |
| `convert-page.test.ts` named pin | Strong | Exact changed Paused value with running and other-control expectations retained |
| `downloader-page.test.ts` named pin | Strong | Exact changed Paused value with other-control expectations retained |
| `queue-cancel-paused.test.ts` | Strong | Actual Convert processing/cancellation states and explicit Downloader seam counts/control |
| `convert-browse-mount.test.ts` | Strong | Forced late chunk setup, exact IPC counts, mounted control and held-request abandonment |

No skip/only/todo masking, assertion bypass or incomplete product placeholder found in these deltas.

## Q6 — Registers, MEU status and docs

Accepted the current register content and tool receipts. `qc-issue-resolve.txt` records the expected baseline register hash, exactly six parsed changed fields under the two named issues, 97/97 decision logs read and zero problems. MEU links were already correct and retained. `qc-status-156.txt` and `qc-status-157.txt` record ready_for_review transitions through meu_status.py; the current YAML and generated surfaces agree. `qc-issue-add.txt` records the F1 issue addition. Independent render --check runs pass for both generators.

HELP-F1-BEFORE-LAZY-MOUNT-LOST describes a real remaining path: AppShell treats all six shell routes as help routes and immediately dispatches the local toggle (`AppShell.tsx:203`); HelpCard subscribes only on mount (`HelpCard.tsx:65`). The queueToggleAfterNavigate storage branch is used only outside those routes. The issue is correctly open, as D-1109 requires, rather than claimed fixed by this change.

The grouping diff changes only section 6 row 89. The actual 06 Tests row and Delivered note correctly describe unchanged AC-97.7 plus the delayed-chunk race tests; 10's Delivered note describes the Processing-only rule, confirm lifecycle and unchanged Transcript Stop. An inherited MEU-157 description still repeats triage's old "AC-97.7 waits for the page" phrase; D-1110, the updated 06 rule, resolution text, delivered test and this report make the actual behavior unambiguous. This is a nonblocking inherited wording observation, not missing implementation or a request to change the approved test.

## Q7 — Safety, fidelity and tested state

The independent `identity.py --state-only` invocation with ELECTRON_RUN_AS_NODE unset returned:

`9d6d172778763fdf61ba3af165dea0243a1e6f9f+a2a427a2dd9bb10693fb1f242ce214ad2b2a3a69d134bac6585795b830bbeb0d`

This exactly equals the gate and prompt value; there is no difference to excuse. The inaccessible global ignore at `~/.config/git/ignore` exposes the sandbox-only `.claude/settings.local.json` entry to enumeration, but identity explicitly excludes that secret path. It was never opened. The existing repository Python interpreter was used directly, without uv synchronization or network access.

The independent audit verifies all 44 scope-copy/absent entries and the 53 baseline EOL entries, unchanged skip-file content, empty index, baseline HEAD and branch main. The current 39 nonsecret changed paths are within the declared files/plan/closeout scope, including post-gate artifacts. The temporary row-3a test is absent. eol-check independently reports 28 paths, zero problems, including the per-line MIXED rules and all named CRLF files.

No newly added content introduces an absolute home-folder path or personal email. Existing historical content, including the old focus history, was left intact; this is a delta-scoped statement, not a claim to have removed historical allowlisted paths. The reviewer performed no repository write, commit, stash, revert, install, build, product-suite run, app launch or network request. The inspected handoff evidence agrees with receipts and the current tested state.

The machine-verdict schema has `additionalProperties: false` and no top-level tested_state property. To remain schema-valid, that exact value is carried in the verdict's identity checklist evidence and in this report.

## Checklist Results

| Check | Result | Observation |
|---|---|---|
| IR-1 runtime evidence | pass | Saved real Electron/backend results inspected and bound to unchanged current identity |
| IR-2 stub compliance | pass | Downloader seam has explicit Processing/Paused/current-job/Resume/cancel-count behavior |
| IR-3 error mapping | n/a | No HTTP handler or error mapping change |
| IR-4 generalization | pass | Both queues and all cancel entry/confirm paths checked |
| IR-5 assertion rigor | pass | Eight test files graded above; no weak delivered test established |
| IR-6 external boundary validation | n/a | No new external input or write boundary |
| IR-7 coverage and deferrals | pass | All 13 + 14 ACs represented; actual Electron proofs; approved F1 exclusion registered |
| AV-1 to AV-6 | pass | Decisive Reds, preserved assertions, exercised changes, no masking/placeholders, source-backed scope |
| Identity, fidelity, skips and EOL | pass | Independent state matches; audit and read-only checkers pass |
| Review-only completion preflight | pass | Canonical task reread; H1-7 verdict is this deliverable; coordinator H1-7a/H1-7b and H2 remain pending as intended |

### Independent command evidence

All following commands ran from `P:/av-kit` through `rtk proxy`, with PYTHONDONTWRITEBYTECODE=1, TMP/TEMP under `C:/Temp/av-kit/queue-convert-fixes/exec-review/tmp`, and ELECTRON_RUN_AS_NODE unset. Saved execution suites were inspected rather than rerun.

```json
{"schema_version":"evidence.v1","check_id":"review-identity","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-17-queue-convert-fixes/identity.py --state-only","cwd":"P:/av-kit","scope":"current D6 inputs","phase":"static","exit_code":0,"result":"pass","tested_state":"9d6d172778763fdf61ba3af165dea0243a1e6f9f+a2a427a2dd9bb10693fb1f242ce214ad2b2a3a69d134bac6585795b830bbeb0d","output":"9d6d172778763fdf61ba3af165dea0243a1e6f9f+a2a427a2dd9bb10693fb1f242ce214ad2b2a3a69d134bac6585795b830bbeb0d; exactly matches saved gate before/after"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-audit","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/queue-convert-fixes/exec-review/audit.py","cwd":"P:/av-kit","scope":"baseline copies, hashes, immutable expectations, saved result recount, gate receipts and scoped safety","phase":"static","exit_code":0,"result":"pass","tested_state":"9d6d172778763fdf61ba3af165dea0243a1e6f9f+a2a427a2dd9bb10693fb1f242ce214ad2b2a3a69d134bac6585795b830bbeb0d","output":"44 scope entries and 53 EOL entries agree with saved bytes; 355 skip files unchanged; Red-bound hashes match with only later MEU-157 insertion removed for the earlier shared-file hash; full UI 140 files / 1614 tests; cancel 2 passed in each of three runs; queue suites 23/26/4 passed; race AC-157.8/.9/.10/.11 each 20; AC-97.7 20; unique sequential passing run numbers and no failed/flaky/skipped outcomes; gate 24 zero-exit steps with receipts; 39 nonsecret changed paths within scope; index empty; baseline HEAD; main; no new home path/personal email; audit: pass"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-browse-probe","command":"rtk proxy node C:/Temp/av-kit/queue-convert-fixes/exec-review/browse-probe.cjs","cwd":"P:/av-kit","scope":"copied browse token logic and native DOM-event acknowledgement semantics","phase":"targeted","exit_code":0,"result":"pass","tested_state":"9d6d172778763fdf61ba3af165dea0243a1e6f9f+a2a427a2dd9bb10693fb1f242ce214ad2b2a3a69d134bac6585795b830bbeb0d","output":"browse probe: 70 histories passed; 100 acknowledged presses leave 0 drop listeners; cancelable acknowledgement and noncancelable negative control passed"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-eol","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-17-queue-convert-fixes/eol-check.py","cwd":"P:/av-kit","scope":"28 scope files, CRLF/LF and per-line MIXED preservation","phase":"static","exit_code":0,"result":"pass","tested_state":"9d6d172778763fdf61ba3af165dea0243a1e6f9f+a2a427a2dd9bb10693fb1f242ce214ad2b2a3a69d134bac6585795b830bbeb0d","output":"eol-check: 28 scope path(s), 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-red-156","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-17-queue-convert-fixes/red-check.py --require AC-156.1 --require AC-156.2 --require AC-156.3 --require AC-156.4 --require AC-156.5 --require AC-156.6 --require AC-156.7 --require AC-156.8 --require AC-156.9 --require AC-156.10 C:/Temp/av-kit/queue-convert-fixes/qc-156-red.txt","cwd":"P:/av-kit","scope":"saved MEU-156 assertion Red and preserved child exit","phase":"static","exit_code":0,"result":"pass","tested_state":"historical Red receipt independently checked at current review","output":"red-check: 1 receipt(s), 10 required test(s), 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-red-157","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-17-queue-convert-fixes/red-check.py --require AC-157.1 --require AC-157.2 --require AC-157.3 --require AC-157.4 --require AC-157.5 --require AC-157.6 --require AC-157.7 --require AC-157.14 C:/Temp/av-kit/queue-convert-fixes/qc-157-red.txt","cwd":"P:/av-kit","scope":"saved MEU-157 unit assertion Red and preserved child exit","phase":"static","exit_code":0,"result":"pass","tested_state":"historical Red receipt independently checked at current review","output":"red-check: 1 receipt(s), 8 required test(s), 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-red-electron","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-17-queue-convert-fixes/red-check.py --require AC-157.8 --require AC-157.9 C:/Temp/av-kit/queue-convert-fixes/qc-157-red-e2e.txt","cwd":"P:/av-kit","scope":"saved Electron picker-count assertion Red and preserved child exit","phase":"static","exit_code":0,"result":"pass","tested_state":"historical Red receipt independently checked at current review","output":"red-check: 1 receipt(s), 2 required test(s), 0 problem(s); original assertions expected 1 and received 0"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-status-render","command":"rtk proxy .venv/Scripts/python.exe tools/meu_status.py render --check","cwd":"P:/av-kit","scope":"MEU generated surfaces","phase":"static","exit_code":0,"result":"pass","tested_state":"9d6d172778763fdf61ba3af165dea0243a1e6f9f+a2a427a2dd9bb10693fb1f242ce214ad2b2a3a69d134bac6585795b830bbeb0d","output":"Drift check passed; SSOT loaded (156 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-issues-render","command":"rtk proxy .venv/Scripts/python.exe tools/issue_triage.py render --check","cwd":"P:/av-kit","scope":"issue generated surface","phase":"static","exit_code":0,"result":"pass","tested_state":"9d6d172778763fdf61ba3af165dea0243a1e6f9f+a2a427a2dd9bb10693fb1f242ce214ad2b2a3a69d134bac6585795b830bbeb0d","output":"OK: known-issues.md is up-to-date"}
```

The independently executed red-check selftest also returned `53 fixture(s) (17 positive, 36 negative), 0 wrong: []`; the independently executed eol-check selftest returned `19 case(s), 0 wrong: []`, both exit 0. These test the checkers, not product behavior.

## Verdict

`approved` — the scoped implementation achieves the registered intent. No substantive findings. Accepted limits remain CANCEL_STALE_POLL and the registered F1 pre-mount gap. This verdict completes the independent review deliverable; coordinator ledger collection, canonical publication, H2 and any separately authorized commit remain the coordinator's work. No push was performed or authorized by this review.
