---
date: "2026-11-08"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-08-light-accent-contrast/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s56-plan-2026-11-08-light-accent-contrast"
round: 2
---

# Critical Review: 2026-11-08-light-accent-contrast

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

Working-tree implementation-plan.md, task.md, the seven plan-local scripts and the targeted production/test/spec sources for Session 56, MEU-126. Applied PR-1 through PR-9 and the Materiality Gate. Independent Codex review of Anthropic's work. HEAD is `f69ee08cb682a409486835b27e432201dac02edb`, on main; implementation remains unstarted.

**Intent anchor:** Session 56 sets the light theme's `--color-accent` to `#155e75` and `--color-accent-hover` to `#164e63`, the values Mat ruled in D-235. With them, white labels on the accent and accent labels on their 12%, 15% and 20% tints read at 4.5:1 or more. A unit test reads the shipped tokens from `styles.css` and computes each ratio, and an E2E proves the built app paints the ruled colours. The dark theme doesn't change. Mat looks at the light theme and says yes before the execution review.

**Intent achieved:** yes as a proposed colour/test design; approval is withheld for concrete execution and data-safety failures below. No disagreement with D-235, D-249, or Mat's right to decide D-455 and D-458.

Only temporary artifacts were written. No product suite, build, baseline, session gate, app, live process-command-line query or network request ran. No prohibited secret file was opened. Whole-checkout identity was not run because the sandbox exposes a normally ignored local settings file; only identity's scratch selftest ran. The coordinator owns the canonical report copy.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | **Row 4 always finds its own checker as a leftover backend.** The Python `-c` source itself contains `'-m avkit_api'`; that source is in the checker's Windows command line. `Get-CimInstance Win32_Process` sees that still-running parent Python, and the unqualified substring arm puts it in `left`. Thus `sys.exit(1 if left else 0)` fails even after Mat approves and every dev-app process has exited. An exact-source synthetic argv probe returned `scanner selects itself: True`, `leftover count: 1`, `validation exit: 1`. It also selects another worktree's backend. This prevents the required human-check row from completing and reaching execution review; violates **AC-126** and its D-458 human-check obligation. Confidence: High. | `docs/execution/plans/2026-11-08-light-accent-contrast/task.md:53`; `implementation-plan.md:321` | Limit the check to the recorded launch's verified process identities/descendants, excluding the checker and its hosts. Retain unrelated processes as informational observations. Prove that a clean launch passes, an owned leftover fails, and the checker, MCP servers and a foreign backend do not count. | open |
| F2 | High | yes | behavior | **Row 4 copies authentication-bearing command lines into its receipt and tool output.** Its diagnostic prints `C(p)[:160]` for every selected process, before cleanup. The real backend launch puts `--token` and `--mcp-token` in argv. A short valid synthetic backend command emitted both token markers through that exact slice. A longer path can still expose a token fragment; truncation is not redaction. A leftover backend, or another worktree's backend selected by the broad filter, therefore leaks credentials into `s56-dev-app-procs.txt` and its subsequent `Get-Content`. This contradicts **NO_RAW_CONSOLE** and PROFILE E5, independently of F1. Confidence: High. | `docs/execution/plans/2026-11-08-light-accent-contrast/task.md:53`; `ui/src/main/python-manager.ts:23`; `implementation-plan.md:137`, `:191`; `PROJECT-PROFILE.md:78` | Print only PID, parent PID and a fixed process-role/ownership label. Keep raw argv out of receipts and tool output; if arguments are essential, redact secret values before any output. Add a synthetic credential diagnostic check. | open |
| F3 | High | yes | behavior | **D-454's save/diff procedure can silently erase a concurrent capture-crop update.** `meu_status.py update` loads the entire YAML, then saves its stale object by truncating/replacing the file, without locking or comparing the current bytes. A peer save between those operations is lost. A before-row copy cannot reveal a peer edit made after that copy: in a temporary-file reproduction using the actual model functions, a peer MEU-128 note existed after the peer save, disappeared after Session 56's stale save, and appeared in neither side of the prescribed before/after diff. Render likewise loads once and rewrites whole generated regions. The allowed ongoing peer activity makes this a real data-loss path in rows 5 and H2-2, not a formatting objection; violates **PR-8**'s read/write atomicity requirement and D-454's preservation obligation. Confidence: High. | `docs/execution/plans/2026-11-08-light-accent-contrast/task.md:38`, `:55`, `:71`; `implementation-plan.md:354`, `:417`; `tools/meu_status.py:131`, `:145`; `tools/meu_status/model.py:214`; `tools/meu_status/render.py:250`, `:301`, `:310` | Serialize these writes with the capture-crop writer, or use a guard respected by all writers spanning fresh read, update, render and verification. Preserve/refuse overlapping edits before replacement. Keep save/diff/disclose as additional evidence, and prove with an interleaved scratch write that the peer change survives or the update refuses. | open |

No Critical finding. These are behavior findings, not control-defeat recurrence claims, so no mechanism slug is assigned. F1 concerns a check that fails incorrectly, rather than a gate bypass.

**Contract-routing exception for Mat:** F1 maps to AC-126. None of AC-43, AC-51, AC-81, AC-94 or AC-126 honestly states credential-output safety or shared-writer atomicity. Accordingly F2 retains `NO_RAW_CONSOLE` and F3 retains `PR-8`, as the review request permits when no registered family fits. Mat must adjudicate that routing; do not silently relabel them as unrelated ACs or claim that the ledger accepted them.

## Review questions

Paths below are relative to `P:/av-kit`; “plan” means the target implementation-plan.md.

### Q1 — Done and arithmetic

Accepted the ruled values and all direct-pair before/after figures. Independently recomputed unrounded WCAG ratios from the shipped token blocks, substituting only the two ruled light tokens in memory:

| Pair | Before | After |
|---|---:|---:|
| White / accent | 3.682043 | 7.266843 |
| White / hover | 5.357755 | 9.114422 |
| Accent / 12% tint over page | 2.978886 | 5.628879 |
| Accent / 15% tint over page | 2.873366 | 5.352369 |
| Accent / 20% tint over page | 2.716107 | 4.963517 |
| Accent / 12% tint over elevated or surface-0 | 3.196913 | 6.055346 |
| Accent / 15% tint over elevated or surface-0 | 3.089743 | 5.765581 |
| Accent / 20% tint over elevated or surface-0 | 2.899729 | 5.310422 |
| Plain accent / page | 3.409437 | 6.728829 |
| Plain accent / white card | 3.682043 | 7.266843 |

The unit design measures shipped tokens, the E2E pins the built app's values, and only the two light lines change. Mat's words remain required. F1 prevents reaching the proposed completed state through its exact row checks; F2/F3 make execution unsafe despite the sound colour design.

### Q2 — TINT_MODEL / D-451

Accepted premultiplied mixing with transparent: the Oklab mix retains the accent colour at the stated alpha, then source-over composition onto the opaque surface gives the stated sRGB calculation. Half-up 8-bit rounding is a useful bounded approximation; the independent +/-1 channel probe confirms 4.914941 for the listed direct pairs. No reviewer Chromium paint measurement was performed.

The assertion that page and white bound every placement is too broad: a selected queue card paints `bg-accent/5` beneath a secondary button (`QueueCard.tsx:66`, `:352`, `:604`; Downloader passes selection at `DownloaderPage.tsx:887`). Its normal/hover ratios are **5.240725 / 4.618892**, still passing. Thus 4.96 is not the live global minimum. A 10% detail-open card would yield **4.364058** on hover, but the complete renderer census finds no production caller passing `detailOpenId`; that state is dormant (`QueueList.tsx:81`, `:217`). I do not block on that hypothetical state or ask to change Mat's hexes. Correct the minimum/bounds prose and consider covering the reachable selected state. No other reachable enabled accent-labelled control below 4.5 was identified, apart from the explicitly open D-455 pill.

### Q3 — CONTRAST_FLOOR / DARK_UNCHANGED / D-450

Accepted. The actual openers are `@theme {` and `:root:not(.dark) {`; `\n}` terminates both even with CRLF. The proposed named-token and six-digit-hex checks reject absent/`var()` values and prevent wrong-block/missing-token vacuity. No 8-bit channel lies between the two luminance thresholds, so 0.03928 versus 0.04045 changes none of these results. Independent helper controls are 21 and **4.542224960** for `#767676` on white. Together with the inspected formula, these are suitable controls; they are not an assertion that two samples prove every possible helper implementation.

### Q4 — RUNTIME_COLOURS / D-452

Accepted as a runnable source-backed design, with runtime execution still pending. The seam answers dark and starts cookie mode at file; the test id is on the radio and `xpath=..` reaches its selected label. Theme buttons select primary/secondary from `uiSettings.theme`. Solid utilities use the token directly, so the expected legacy `rgb(...)` serialization is appropriate. `toHaveCSS` polling handles transitions (the current duration token is 120 ms); moving to (0,0) clears the button hover, and explicit hover tests the separate hover token. A separate app/temp profile and unchanged seam keep AC-94.7 and peer tests independent. No added test id is necessary.

### Q5 — MATRIX_REBASELINE / D-456

Accepted all **40** moves, not only a sample. A separate implementation derived 0 mismatches against all 160 shipped rows and exactly matched EXPECTED_MOVES after substitution. Examples: Pending label checkbox/detail **10.95→10.74 / 10.40→10.04**; AgeRestricted icon **7.27→7.13 / 6.87→6.64**. The replica, floors, negative controls, ruled-token check, in-place hash guard and numeric-span rewrite match AC-43.3. The rewrite retains the CRLF and untouched bytes; `_meta` remains 80/80 labels, worst 6.61, four icons below advisory, worst 1.94. Selftest and shipped control passed. AGENTS.md:57 and the A-6 precedent support the described explicit authorization before changing pinned data; this review does not supply Mat's “proceed.”

### Q6 — Callers, fixture and D-455

Accepted the eleven existing unit callers plus the new test and settings E2E. The renderer/test census found no additional Python, MCP or snapshot dependency on the literal light values. queue-slot-baseline.json stores utility/var references rather than resolved hex colours, so no re-baseline is needed. Every D-455 table figure agrees with independent calculation, including Generating light **3.972989→2.013078** and dark **1.298495**. A/A' fix Generating in both themes but leave the other pill defects; B records that wider defect and C leaves it unrecorded. The options and additional implementation/test/review costs are fairly described. No other independent text label on the solid accent was identified; labels inherited inside primary buttons are already covered.

### Q7 — Red and controls

Accepted the required unit Reds and their measured pre-change values: .1/.3/.4/.5/.6 fail assertions, while .2/.7 pass as guards; the ruled pair makes all direct assertions pass. The specified AC titles and `--require` boundaries are compatible, and the E2E `-g` selects the proposed .8. Dark positive steps precede the expected light mismatch. red-check's 38 fixtures passed, including CSS assertion acceptance and explicit launch/action/setup refusal. Its selftest is evidence about receipt recognition, not a real Red run. Session-gate captures child exits and fails fast. **Not accepted:** row 4's exact check cannot pass (F1). No additional materially false-passing deliverable check was demonstrated.

### Q8 — Endings, identity and scope

Accepted the byte-preservation instructions and token check. Independently observed CRLF/bare-LF counts: styles **211/0**, settings **889/0**, matrix **1138/0**, 06-gui **1628/0**, grouping **322/0**. Row 3 checks both exact new lines and the two expected zero-context hunks; unchanged index/HEAD and S3 bind that to the baseline. The matrix writer edits only number spans. identity's scratch mutation selftest passed, binding code/tests/config, scripts, matrix, registers/renders, peer inputs and runtime while excluding the listed closeout outputs. Plan/task Markdown is excluded even though task-contract reads task.md: this identity does not certify an unchanged task-lint input; rerun that check if the task changes. No concrete missing product deliverable follows from that exclusion here. scope-paths covers the inventoried writes, the existing dirty paths and plan/review/reflection prefixes, and explicitly refuses test-ids.ts. Those prefixes are intentionally broader than individual filenames.

### Q9 — Shared files and dev-app cleanup

The ordinary serialized YAML update preserves every existing peer MEU record; the scratch probe confirmed that. Saving and diffing also exposes ordinary reformatting or render changes to lines already present in the copy. **Not accepted:** it cannot catch the interleaved lost update reproduced in F3. The render operations have the same unguarded read/replace shape. D-454 needs writer serialization or an effective conflict guard.

The prose allows stopping only this launch's descendants and leaving other processes alone; it does not authorize killing an arbitrary match. **The actual check nevertheless selects its own Python checker and foreign-worktree backends** (F1), while correctly excluding the ordinary Electron MCP command. Launch ancestry must govern the completion predicate too. The process diagnostic also leaks argv (F2). Do not run that raw command as written.

### Q10 — Safety

Accepted the absence of new remote media/network work in the colour change: unit reads are local, the settings seam answers renderer requests, sync is offline, and audits/downloads are excluded. The dev app's local backend is the prescribed human-check environment. No YouTube write/upload path is introduced. The reviewer used only local files, scratch data and synthetic argv. **Not accepted:** the claim that no new raw stdout/receipt value is introduced; F2 traces backend secret arguments directly to the new process diagnostic. Product log statements themselves remain unchanged.

## Checklist Results

These assess plan readiness; no future Green or full product gate is claimed.

### Information Retrieval (IR)

| Check | Result | Observation |
|---|---|---|
| Scope, sources, PR-2 | pass | Targeted issue/MEU/06/grouping reads agree; current light tokens and absent new test/handoff confirm unstarted work. |
| Executable existence | pass | All seven plan-local scripts are present and inspected. |
| Author independence | pass | Codex reviews Claude Code/Anthropic's plan; no self-authored approval. |

### Design Review (DR)

| Check | Result | Observation |
|---|---|---|
| PR-1, PR-3 — Alignment | pass | Baseline → both Reds → token/matrix Green → Mat → records → review/closeout is consistent. |
| PR-4, PR-8 — Execution and guards | fail | F1 gives deterministic exit 1 on an empty dev-app process set; F3 loses a peer write invisibly. |
| PR-5, PR-7 — Source and scope | pass | Ruled tokens, no riders and the open pill decision are preserved. No additional preference is imposed. |
| PR-6 — Corrections readiness | pass | Same plan/task can specify safe cleanup and serialized shared writes; round-2 census is not applicable yet. |
| PR-9 — Contracts | pass | Named contracts identify the operative rules; the overly broad surface/minimum claim is non-blocking prose drift. |
| Output safety | fail | F2's synthetic argv fixture emits both credential markers through the specified slice. |

### Post-Implementation Review (PR)

| Check | Result | Observation |
|---|---|---|
| Contrast, matrix and helper design | pass | Independent calculations and script controls agree. |
| Fresh product Red/Green/full gate | n/a | Prohibited in this read-only review. |
| Review write/egress boundary | pass | Only C:/Temp/av-kit writes; no live app, secret file, process-argv query or network access. |

### Decisive evidence

All commands below ran from P:/av-kit with PYTHONDONTWRITEBYTECODE=1 and all-stream temporary receipts; selftests also used TMP/TEMP under C:/Temp/av-kit. Exact command exits were retained before receipt reads. Probe exit 0 means the reproduced observation/assertion succeeded, not that the plan passed.

```json
{"schema_version":"evidence.v1","check_id":"independent-contrast-matrix-and-secret-fixture","command":"rtk proxy python C:/Temp/av-kit/s56-probe.py","cwd":"P:/av-kit","scope":"local token arithmetic, independent AC-43.3 replication, synthetic argv only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f69ee08-working-tree-plan-review","output":"white/accent 7.266842817; white/hover 9.114421862; direct tint minimum 4.963517113; +/-1 minimum 4.914940756; selected-card hover 4.618891803; dormant detail-open hover 4.364057965; 0/160 shipped matrix mismatches; 40 moves match EXPECTED_MOVES; both synthetic secrets emitted=True"}
{"schema_version":"evidence.v1","check_id":"row4-self-match","command":"rtk proxy python C:/Temp/av-kit/s56-process-probe.py","cwd":"P:/av-kit","scope":"exact task row-4 scanner source represented as Windows argv; synthetic processes","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f69ee08-working-tree-plan-review","output":"exact source extracted=True; scanner selects itself=True; with no app/backend leftover count=1, validation exit=1; foreign worktree backend selected=True; avkit MCP selected=False"}
{"schema_version":"evidence.v1","check_id":"shared-yaml-lost-update","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s56-race-probe.py","cwd":"P:/av-kit","scope":"actual meu_status.model load/update/save on a temporary copy only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f69ee08-working-tree-plan-review","output":"peer marker before=False; after peer save=True; after stale Session 56 save=False; saved before/after diff mentions lost peer marker=False; initial peer records retained=True"}
{"schema_version":"evidence.v1","check_id":"matrix-selftest","command":"rtk proxy python docs/execution/plans/2026-11-08-light-accent-contrast/matrix-rebaseline.py --selftest","cwd":"P:/av-kit","scope":"matrix refusal cases and in-memory CRLF round trip","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f69ee08-working-tree-plan-review","output":"matrix-rebaseline selftest: 0 failure(s)"}
{"schema_version":"evidence.v1","check_id":"matrix-shipped-control","command":"rtk proxy python docs/execution/plans/2026-11-08-light-accent-contrast/matrix-rebaseline.py --check-shipped","cwd":"P:/av-kit","scope":"shipped token-to-matrix control","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f69ee08-working-tree-plan-review","output":"matrix-rebaseline --check-shipped: 0 of 160 rows differ"}
{"schema_version":"evidence.v1","check_id":"red-recognizer-selftest","command":"rtk proxy python docs/execution/plans/2026-11-08-light-accent-contrast/red-check.py --selftest","cwd":"P:/av-kit","scope":"receipt parser fixtures only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f69ee08-working-tree-plan-review","output":"38 fixtures: 12 positive, 26 negative, 0 wrong"}
{"schema_version":"evidence.v1","check_id":"identity-selftest","command":"rtk proxy python docs/execution/plans/2026-11-08-light-accent-contrast/identity.py --selftest","cwd":"P:/av-kit","scope":"scratch repository binding/exclusion mutations only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f69ee08-working-tree-plan-review","output":"identity selftest: 0 failure(s)"}
```

Manual observer for source/call-chain assessments: `codex-independent-reviewer`; procedure: read the cited working-tree definitions and trace each consumer/validator, compare against the plan/task, then verify the reported counterexamples in the synthetic probes above. Manual observations have null exit status. No full D6 identity is asserted by the descriptive tested_state above.

## Verdict

**changes_required.** The ruled colours and proposed contrast/matrix tests are sound. Correct the row-4 completion predicate and credential output, and prevent overlapping shared-file writes from erasing capture-crop work. Route F2/F3's honest contract identifiers to Mat as the request prescribes. D-455 remains Mat's open preference decision, not an additional finding. The 4.96 minimum/bounds prose should acknowledge the passing 4.62 selected-card case. No repository correction was made.

## Corrections Applied (2026-11-08)

Written by the coordinator (Claude Code), not the reviewer. Every plan cite is to `docs/execution/plans/2026-11-08-light-accent-contrast/implementation-plan.md` as it reads for the recheck.

| Finding | Change | Status |
|---|---|---|
| F1 | Row 4's inline checker is replaced by the plan-local `dev-app-procs.py` (`LAUNCH_OWNERSHIP`, new AC-126.9). `record` stores the launched tree as process id and creation time; `check` counts a process only when the record holds it with the same creation time or it descends from a recorded process and started no earlier than its parent. The checker, the processes it runs under and the ones it starts never count, and neither do the avkit MCP servers. Plan :141, :233, :327-342, :382 (S12); task row 4. | fixed, pending verification |
| F2 | `dev-app-procs.py` prints and records each process as its id, its parent's id, a role and an owner only: no command line, argument or executable path (`NO_RAW_CONSOLE` now covers plan-local scripts). A selftest case feeds a synthetic backend argv with `--token` and `--mcp-token` and asserts neither reaches the output or the record. Plan :140, :194-196, :233. | fixed, pending verification |
| F3 | Row 5 and H2-2 write the three status files only through the plan-local `status-write.py` (`GUARDED_STATUS_WRITE`, new AC-126.10). It holds all three with an exclusive handle from its first read to its last write, runs the status tool's own update and render on staged copies, refuses any change outside MEU-126's entry and the generated regions, keeps the bytes it read, and writes the diff and the disclosure. `--verify` runs at H1-3 and before H2-5. Plan :142, :234, :285-296, :381 (S11), D-454 :433-442; task rows 5, H1-3, H2-2, H2-5. | fixed, pending verification |
| Q2 note | A selected queue card's 5% wash over the page is in `TINT_MODEL` and in AC-126.3 and AC-126.4; the unit test imports `CARD_STATE_CLASSES` and reads the wash alpha from the class. Worst pair 4.62 (hover), 4.54 with the one-step margin (`C:/Temp/av-kit/s56-plan-selected-card.txt`). The detail-open card (4.36) has no caller and is in Out of Scope. Plan :120-122, :283, D-451 :403-412. | fixed, pending verification |
| Q4 note | The E2E text gives the 120 ms transition (`--duration-fast`, `styles.css:62`). Plan :171. | fixed, pending verification |
| Routing | Mat ruled on the routing on 2026-11-08 ("all recommendations accpeted, proceed"): F1 under AC-126 as the review mapped it, F2 under AC-126.9 and F3 under AC-126.10 (D-459, plan :474-484). In the same message Mat chose B for D-455 (plan :463-473). | accepted by Mat |


## Recheck (2026-11-08)

### Prior Pass Summary

| Finding | Prior Status | Evidence | Recheck Result |
|---|---|---|---|
| F1 | open | `dev-app-procs.py:121-154`, `:171-206`; `task.md:53`; plan `:233`, `:332-338`. Re-ran the selftest: clean quit passes, owned leftover/orphan fails, reused IDs and checker/hosts do not count. Independently checked a later backend directly under recorded Electron, both external MCP launch forms and another worktree's app/backend. The old self-match and foreign-backend failure are removed; scope limits are stated in R1. | closed |
| F2 | open | `dev-app-procs.py:77-90`, `:157-181`, `:281-289`; plan `:140`, `:196`, `:233`. Re-ran the synthetic credential case: `leaked []`. Independently injected PowerShell failure with secret-bearing captured stdout/stderr and invalid JSON: neither exception traceback emitted those markers. No raw process field is serialized into the record or report. | closed |
| F3 | open | `status-write.py:66-108`, `:171-246`, `:249-256`; `task.md:55`, `:59`, `:71`, `:74`; plan `:234`, `:289`, `:381`, `:438-442`. Nine selftest cases passed; dry write/verify on copies passed. An independent subprocess using the real status model loaded during the hold, then its save exited 1 with `PermissionError`. Preservation and stale-save controls reproduced the intended failures. | closed |

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Answers

Paths in this section are relative to the session plan folder unless a repository path is given. This is an independent Codex recheck of Claude Code/Anthropic's corrections. Report round 2 is ledger round 1. D-459 now states the routing honestly: both new script contracts belong to family AC-126. Previously accepted Q1, Q3–Q8 and Q10 stand except for the corrections examined here. No High or Critical delivery defect remains demonstrated.

**R1 — Accepted for the prescribed real launch, with bounded ancestry evidence.** `record` waits for Electron and the backend, then stores PID, parent PID, creation time and fixed role (`dev-app-procs.py:171-206`), covering npm's staged startup rather than recording the shell alone. `classify` checks recorded creation times, follows later children, retains exited recorded parents as orphan roots, excludes the checker/its ancestors/descendants, and leaves unrelated processes alone (`:94-154`). The independent restart case, a new backend directly under the recorded Electron whose parent has since exited, remains owned. Clean quit returns 0; an owned remaining process returns 1. `--stop` snapshots again and compares creation time before each PID signal, then checks again (`:209-223`). The supplied live stand-in receipt shows 3 live, then 2 orphans, then 0 after stopping; I did not run live process enumeration or stop a process.

This is not an unconditional history of every process ever spawned: an unrecorded intermediary that both starts and exits between snapshots loses its descendants' ancestry. Also, the explicit MCP-role exclusion recognizes Electron, not node (`:65-74`): a synthetic node MCP below a recorded app parent would count. Both actual MCP forms launched outside the app tree remain untouched. The app's production launch spawns the backend directly (`ui/src/main/index.ts:232-264`); its child-exit path retires ownership rather than launching a replacement intermediary (`:295-309`), and it does not spawn the MCP server. Thus these synthetic limits do not establish a failure in row 4's current production call chain or reopen F1's removed self-match. No stronger universal ancestry/MCP claim is certified.

**R2 — Accepted for process data and credentials.** Only fixed-role/ownership text and integer identities are printed; the record adds creation time and timestamp, without argv or executable paths (`dev-app-procs.py:157-181`, `:199-205`). PowerShell stdout/stderr stay captured; a `CalledProcessError` renders the fixed query, not captured output. JSON-decode errors do not render the document. The independent fault controls confirmed both properties. The selftest really includes `--token`, `--mcp-token`, their values and a synthetic home path, and tests the report and record, rather than simply checking an empty output. Ordinary Python traceback source-file locations and CLI error/help text are not globally scrubbed: this acceptance concerns raw process data, not a guarantee that arbitrary failure output contains no filesystem location whatsoever.

**R3 — Accepted.** `FILE_SHARE_READ` permits readers but denies writes/replacements/deletions. Handles are acquired in fixed YAML → BUILD_PLAN → registry order, all before the first read (`status-write.py:55`, `:87-93`, `:176-183`). A pre-existing writer causes refusal before any write; partially acquired handles close through `ExitStack`. A peer save completed before acquisition is read fresh; there is no unlocked read between acquisition and staging. The peer's actual unlocked `model.load` can succeed while held, but `model.save`'s `open('w')` fails loudly; the independent child-process control observed exit 1 and `PermissionError`, not a silent ignored update (`tools/meu_status.py:131-145`, `tools/meu_status/model.py:194-225`).

Staging calls the tool's own update/save/render/check functions; out-of-entry/out-of-region changes refuse before replacing real bytes (`status-write.py:193-223`). Measured current LF/CRLF counts are YAML **3491/0**, BUILD_PLAN **161/0**, registry **228/0**, with no bare CR. The dry write kept those LF endings, changed only MEU-126 in YAML, and disclosed the removed and added BUILD_PLAN total lines. Rendering generated regions from YAML is intentional, not preservation of arbitrary hand-edited generated content. A stale peer save after release remains possible; `--verify` detects a dropped expected status or render drift at H1-3 and before H2-5, as described. It is detection at those checkpoints, not a session-long transaction. S11's wait-and-retry-once for a refused write, and immediate stop/report on verify failure, are appropriate.

**R4 — Accepted as a test design; no Vitest execution claimed.** Re-ran the selected-card probe: 5% wash over page, then 12% tint gives **5.2407**; 20% gives **4.6189**; the two-stage one-step worst case is **4.5352**, rounding to 4.54. `CARD_STATE_CLASSES` is a real named export, consumed by the reachable selected Retry card. Vitest collects the proposed `.test.ts`, supports the existing jsdom file directive and TSX imports; `ui/tsconfig.json:7` sets `react-jsx`, and existing queue tests already import this module. The planned explicit throw for absent `bg-accent/N` prevents a missing class from becoming an empty passing iteration (plan `:158`, task `:50`). No production renderer caller supplies `detailOpenId`; the list derives `detailOpen` only from that prop. Its 4.3641 hover remains dormant, not a reason to change the ruled hexes. `styles.css:62` is **120 ms**; polling CSS assertions cover the transition.

**R5 — Accepted as executable instructions, without overstating mechanical enforcement.** Rows 0/1/4/5/H1-3/H2-2/H2-5, baseline `:107-111`, AC-126.9/.10 and S11/S12 agree on script names, statuses, sequencing and receipts. Both added baseline selftests use `Invoke-Step`, which preserves and propagates failure. Row 4's final checker propagates its exit; row 5 and H2-2 require a fresh successful write receipt and then check the renders; H1-3 propagates verify failure before its next command. H2-5 puts verify and its S11 stop in the task instruction, while its validation cell only writes the commit draft: that cell alone is not a mechanical proof that verification passed. Likewise record failure must trigger S12 before asking Mat. The plan explicitly requires those stops; the draft neither authorizes nor performs a commit. No new materially missing product deliverable or permitted bypass of those stops was demonstrated.

Non-blocking prose notes: plan `:111` says a "no" reverts rows 1–3 while `:341` retains them; both stop before records and further changes require Mat. The dry-run disclosure is two diff lines for one changed total, rather than one emitted line (`:291`). These do not change the approved colour work or require another review round.

**R6 — Accepted within the exact prescribed invocations.** Neither script has a network request path. The CIM query is local; only `check --stop` signals processes, after ownership classification and a fresh creation-time check. The stated row commands put records, staging, kept bytes and diffs under C:/Temp/av-kit, with only the three status files replaced in the repository. These scripts are not a general filesystem sandbox: `--out`, `--keep` and `--diff-out` are caller-selected paths; supplying different paths can write elsewhere, and `--keep` removes an existing staging directory. The plan's fixed arguments matter. The node-MCP/ancestry limits in R1 apply to the blanket ownership claim. No real process was stopped, no live argv snapshot was requested, and no forbidden file, product suite, build, baseline, gate, app or network operation was run in this review.

Recheck evidence, all from P:/av-kit: `rtk proxy uv run python .../dev-app-procs.py --selftest` exited **0**, **0 failures**; `.../status-write.py --selftest` exited **0**, **9 cases/0 failures**; `rtk proxy uv run python C:/Temp/av-kit/s56/status-write-dry.py` exited **0**, write **0 problems**, verify **0**. `rtk proxy uv run python C:/Temp/av-kit/s56/recheck-probe.py` exited **0** after repairing the probe's artificial traceback-marker setup; it confirmed restart ownership, external MCP/foreign exclusion, nonleaking captured-error controls, byte counts and the real peer save refusal. `rtk proxy python C:/Temp/av-kit/s56/selected-card-probe.py` exited **0** with the figures above. These uv runs set `PYTHONDONTWRITEBYTECODE=1`, TMP/TEMP under C:/Temp/av-kit/s56/tmp, `UV_OFFLINE=1`, `UV_NO_SYNC=1` and `UV_CACHE_DIR=C:/Temp/av-kit/s56/uv-cache`. Initial uv attempts exited **2** at the sandbox-inaccessible home cache; those were environment failures, not script-test results. No product Red/Green or full D6 pass is claimed.

During the recheck, `main` advanced from the supplied `f69ee08` to **75617379f63c0885024b2c9f0dd9fc72de854b8b**. `git diff --name-only f69ee08 HEAD` shows only capture-crop grouping/inspiration/spec/status files; no reviewed product or plan-local script changed in that commit. The shared-file probes read the current working files. Row 0 must establish its fresh execution baseline. No whole-checkout identity or git status was run; this sandbox cannot read `<HOME>/.config/git/ignore`, which normally hides `.claude/settings.local.json`; that settings file was not opened. Manual source observations: observer `codex-independent-reviewer`, procedure targeted reads and call-chain/command comparison, exit null. Only temporary files were written; the coordinator owns canonical report publication and ledger recording.

### Verdict

**approved.** F1, F2 and F3 are closed, both prior notes are addressed, and no evidence-backed High or Critical defect prevents the corrected plan from delivering its stated intent. This approves the plan; execution still awaits Mat's next message and the later D-458 visual approval.
