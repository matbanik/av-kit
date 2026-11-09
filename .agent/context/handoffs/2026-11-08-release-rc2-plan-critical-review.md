---
date: "2026-11-08"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s57-plan-2026-11-08-release-rc2"
round: 3
---

# Critical Review: 2026-11-08-release-rc2

> **Review Mode:** `plan`
> **Verdict:** `changes_required`

## Scope

Independent Codex review of Claude Code/Anthropic's unstarted Session 57 plan, task and plan-local scripts, against MEU-125's cited contracts and targeted production sources. Applied PR-1 through PR-9 and the Materiality Gate. Repository files were read only; all reviewer writes are under `C:/Temp/av-kit`. No network request, product suite, build, installer, packaged smoke or live audit was run. The sandbox-only untracked `.claude/settings.local.json` was disregarded and never opened.

**Intent anchor:** Session 57 moves every version surface to 0.1.0-rc.2, adds the libdvdcss line to the notices, builds the installer from a clean tree with the pinned FFmpeg, checks it as RC1 was checked plus MEU-114's round trip on the full build and MEU-117's and MEU-121's packaged smokes on the installer's own backend, runs a fresh gate, and writes the notes and the publish checklist. Nothing is tagged, uploaded or published: those steps are Mat's, and the checklist gives them in order.

The delivery sequence largely serves that intent, but the clean-tree check admits a forbidden baseline change, the proposed audit authorization omits real traffic, the build can download on a cache miss, and the default Transcript wording retains a held claim.

## Findings

Paths are relative to `P:/av-kit`. All findings have High confidence. F1/F3/F4 concern the release deliverable; F2/F5 concern committable tooling.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | **D-464 authorizes an incomplete traffic inventory.** The table says the two other videos never start and omits all model/asset fetches. The actual authoritative audit selects ONNX, calls `models.download` into its isolated models directory, waits for voice packs, and provisions vocabulary/spaCy assets. It also starts video C before cancellation. An acceptance of “exactly these” requests therefore permits a gate that immediately makes undisclosed downloads, contrary to the plan's network boundary and AC-125.19's D-464 authorization. `AUDIT_RULE` cannot make the brief true. | `implementation-plan.md:91`, `:96`, `:99`, `:102`; `mcp-server/scripts/audit/fixtures.ts:24`; `mcp-server/scripts/audit/plan.ts:584`, `:632`, `:912`; `packages/infrastructure/src/avkit_infra/model_manager/manager.py:76`; `packages/infrastructure/src/avkit_infra/tts/assets.py:77` | Enumerate model weights, voice packs, vocabulary, spaCy and the started/cancelled media, including source hosts and the playlist metadata fetch in the direct proof. Reconcile the no-model-download statement and obtain Mat's decision on the actual traffic, or change the audit design to stay within the authorized boundary. | open |
| F2 | High | yes | control-defeat | **`CLEAN_TREE` never consults baseline-dirty paths.** It accepts any changed allowed filename. A scratch repository with a foreign `ui/package.json` change already listed in `baseline-dirty.txt` returned exit 0; adding the rc.2 version edit still returned 0 while preserving that foreign change. Row 3 can consequently build another session's change without the required HDP. Violates AC-125.5 and D-462. **mechanism: task-row-completion-predicate** | `docs/execution/plans/2026-11-08-release-rc2/clean-tree.py:68`, `:74`, `:163`; `implementation-plan.md:145`, `:267` | Read the baseline ownership evidence and refuse pre-existing foreign changes even when their paths are version surfaces. Explicitly distinguish the session-owned plan folder from foreign baseline changes. Add this concrete negative case to the scratch selftest. | open |
| F3 | High | yes | behavior | **The “offline” build falls back to downloads instead of S13.** Row 3 invokes normal `dist:prep`/`dotnet publish` and electron-builder without a cache-only or network-blocking boundary. The installed builder's cache-miss branch calls `downloadArtifactToFile`; the planning cache census does not turn that branch off. If a toolset cache is missing or invalid at build time, the build downloads before it can report S13 and can still exit 0. This violates `FRESH_BUILD`'s stated offline execution boundary, AC-125.6 as specified at plan lines 169–171, and task S14. | `docs/execution/plans/2026-11-08-release-rc2/build-rc.ps1:66`, `:71`; `ui/package.json:23`; `ui/node_modules/app-builder-lib/out/util/electronGet.js:498`; `implementation-plan.md:169`, `:440`; `task.md:40` | Make the build fail closed offline, including NuGet restore, Electron/builder toolsets and uv/npm invocations. Use cached inputs with an enforced no-egress boundary or cache-only resolution, and prove a missing-cache refusal in scratch without making a request. | open |
| F4 | High | yes | behavior | **The unanswered D-466 fallback retains the claim D-216 holds.** Row 8 automatically takes “RC1's wording plus one line” if Mat has not answered. RC1's wording includes “YouTube is limiting your network, not your copy of av-kit.” Appending that the other-network check has not run leaves the unverified diagnosis in the new notes. Row 8's needles accept it. This violates `RELEASE_NOTES`, AC-125.20 and 07:383; it can mislead Transcript users while the wider failure remains unexcluded. | `implementation-plan.md:113`; `task.md:59`; `docs/releases/v0.1.0-rc.1.md:56`; `docs/build-plan/07-distribution.md:383`; `.agent/context/known-issues.yaml:3630` | Until a decisive other-network result exists, retain the measured maintainer-network block and the unverified-path warning, but omit the held “your network, not your copy” diagnosis. Make that the unanswered fallback and accurately describe it in D-466. | open |
| F5 | Medium | no | behavior | **`NO_RAW_CONSOLE` overstates home-path protection.** The round-trip logs the expanded updater path even in preconditions-only mode, and the expanded roaming-data path on every full run. Those resolve under `<HOME>` and enter the receipt/stdout that the handoff may quote. This is a concrete home-path disclosure, but no credential or committed-record disclosure was demonstrated. | `docs/execution/plans/2026-11-08-release-rc2/install-roundtrip.ps1:349`, `:372`; `implementation-plan.md:158`, `:233` | Replace home prefixes with `<HOME>` before logging and keep handoff excerpts sanitized. Preserve counts, fixed role labels and hashes. | open |

Blocking contracts route to family **AC-125**. F2 uses the supplied closed mechanism vocabulary; the others describe behavior rather than mechanism-recurrence claims. No Critical finding.

## Review questions

### Q1 — Done and installer versions

Accepted the version inventory against the targeted source census. The 13 edits cover the manifests/locks, MCP identity, Python package/API identity, OpenAPI and notice URL. electron-builder reads `ui/package.json`'s version (`appInfo.js:29`); the configured artifact template uses it (`ui/electron-builder.yml:16`). No independent rc.1 installer display/update-version override was found. Fresh generated outputs therefore derive rc.2 from a bumped surface.

The build-record identity deliberately survives documentation/status changes and compares committed inputs with `--ref HEAD`. **“With the build record committed” remains conditional on Mat's actual commit and the post-commit verification in H2-5** (`task.md:81`); writing a draft and passing pre-commit checks do not establish Done. F2–F4 prevent accepting the intended completed release as currently planned.

### Q2 — VERSION_ONE and NOTICE_LINE

Accepted all 13 edits, replacement counts and line endings: independent dry-run wrote 13 scratch copies and reported 0 problems after. The existing archive name is the deliberate exception. The supplied offline lock receipt shows the unchanged and fully bumped locks pass, while manifests-only fail. The notices line agrees with the binary strings and the registered static-link recipe; no FFmpeg repin is needed.

D-465 A is sound: retarget the release URL and attach the unchanged archive under its existing name. The archive size/hash and AC-110.21 needle are accurately cited. B retains the stated dependency on RC1's assets. C is extra reassembly work; renaming the existing archive alone would not satisfy the pinned `ARCHIVE_NAME` test. No request was made to verify any remote source.

### Q3 — Red and guard selection

Accepted the eight required test names. Each version assertion reads a currently rc.1 surface against the changed constants; the notices tuple fails its new URL/library needles. The scripted Green supplies the matching bytes without changing tests. `-k "ac_110_20 or ac_110_21"` selects the intended existing function names. Red-check's 38 fixtures passed, including assertion acceptance and setup/collection/launch-error refusal. This establishes parser/design readiness, not an executed product Red.

### Q4 — Clean tree, fresh build and record

Accepted NUL-separated path handling, deleted/rename detection and HEAD binding. **Not accepted:** baseline ownership is absent from the actual check (F2). The built-in nine cases pass but do not cover that failure.

Accepted cached-pin extraction with SHA checking, real backend packaging without `--stub-ok`, licence generation after picker preparation, `--publish never`, the size refusal and `--expect-inputs`. The temporary-index identity, installer hash verification and S8 rebuild of rows 3–7 appropriately bind a changed product tree to a new installer. **Not accepted:** cache presence alone enforces no-download behavior (F3).

### Q5 — Packaged checks and round-trip safety

Accepted the RC1 root smoke/negative control, MCP version probe and offline TTS phase. Phases A–D match AC-114.5–.9. The actual phase-A contract is the uninstall negative control; only B–D invoke the new-version app smoke. B copies the installed backend, compares file count/bytes/exe hash, and rows 6–7 use that copy with dead proxies and WAV-payload checks. These are the requested AC-117.15/AC-121.8 checks.

The preconditions protect existing installs/shortcuts/registry entries and refuse a running av-kit; process stops use a directory-bounded executable path, excluding checkout MCP servers. The custom uninstall only deletes the updater's known installer and removes an empty directory. Real app data is not used for launches. Limits: the advertised existing-`installed-backend` precondition is absent (the script replaces this scratch copy at `:279`); roaming protection is folder-existence only, while local data compares top-level names. Also, the app-smoke Settings visit reaches the real default models-folder writability probe (`SettingsPage.tsx:333`, `setup-readiness.ts:109`): it creates/removes a probe file there because only `AVKIT_APP_DATA`, not the child home, is isolated. No model deletion/download or lasting data loss was demonstrated; do not describe models as completely untouched.

### Q6 — Audit rule

Accepted the paused start/resume shapes, exact block message/observable, dependency chain and changed transcript deltas. Its 46 selftests passed. The gate clears the old summary first, passes this HEAD, and only reaches the live proof after structural/source checks. Other failures or missing proof are refused. A tolerated result remains non-pass in the audit report and prints `INCOMPLETE VERIFICATION`; handoff/notes are explicitly required to carry that distinction. **Not accepted:** the traffic table or its no-model-download claim (F1).

### Q7 — Notes and publish checklist

Accepted the corrected models path, cached source attachment, RC1-fate decision and stated order: commit/push/record verification/tag/draft/attachments, clean-machine and Transcript checks, then publish and RC1 action. No new instruction publishes ahead of the clean-machine check. Local `gh ... --help` confirms draft editing, notes-file replacement and optional tag cleanup; D-467 A must preserve the old body while adding its line and explicitly use `--latest=false`. Retaining assets under A keeps the source beside RC1; drafting/deleting removes their public availability as described.

The needle checks establish required facts, not prose truth or step ordering by themselves; the named independent document review remains necessary. **Not accepted:** D-466's automatic fallback (F4). Its recommendation to obtain an actual other-network result is otherwise safe and does not authorize a reviewer request.

### Q8 — Shared records and scope

Accepted `status-write.py`'s Windows handles across the initial read, staged update/render and final writes, plus per-entry/region diff refusal and readback. Its selftest passed, including interleaving/refusal and the unguarded lost-update control. Grouping row 57 is at line 260; a row-scoped byte replacement preserves 322 CRLF lines. The D3 note fits between the residual table and separator. Identity includes release documents, build record, register/render/grouping inputs, while excluding listed closeout artifacts; scope-paths covers the inventoried writes. H1-6b correctly requires rerunning the gate when the post-gate notes change their bound input. Broad allowed prefixes do not by themselves prove that every edit is within its promised line scope.

### Q9 — Gate and watch item

Accepted the implemented static/full/runtime step inventory and fail-fast exit propagation against §5. D-470 states the requested single unchanged rerun and the second-failure fix before release. The coordinator must archive the first run's fixed-name receipts before rerunning; the script does not archive them automatically. The demonstrated material false-pass is F2. No product gate was run or inferred from helper selftests.

### Q10 — Safety and value flow

Accepted the absence of autonomous tag/upload/release/YouTube-write commands and the unchanged product logging lines. FFmpeg extraction is cache-only; the two installed-backend TTS smokes explicitly block external requests. **Not accepted:** the audit's stated request boundary (F1), the build's cache-miss boundary (F3), or the claim that helper output cannot contain a home path (F5). No actual request or secret read was needed to establish these call chains.

## Checklist Results

These are plan-readiness observations, not future execution evidence.

| Check | Result | Observation |
|---|---|---|
| PR-1/2/3/5/6/7: alignment, unstarted scope, task contract and sources | pass | Plan/task agree on the single MEU, dependency order, human gate and no-publish scope; task rows are unstarted and sources are explicit. Existing script files were inspected. |
| PR-4/8: material control behavior | fail | Scratch baseline-dirty input bypasses CLEAN_TREE; source call chains show undisclosed audit downloads and build download fallback. |
| PR-9 / process-paperwork observations | n/a | No paperwork or repeated-literal issue is elevated into a delivery finding. |
| Version/edit readiness | pass | Scratch dry-run: 13 files, exact endings/counts, 0 problems after. |
| Read-only helper selftests | pass | Red-check 38 fixtures/0 wrong; identity 0 failures; build identity passed; audit rule 46/46; guarded status 0 failures; clean-tree 9/9 with scratch-commit signing disabled. |
| RELEASE_NOTES fallback | fail | Unanswered D-466 retains RC1:56 despite 07:383 holding that diagnosis. |
| Product Red/Green, build, installer and full gate | n/a | Forbidden during this review; not run. |

### Reproducible evidence

```json
{"schema_version":"evidence.v1","check_id":"review-version-dry","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-08-release-rc2/version-bump.py --dry-run C:/Temp/av-kit/reviewer-s57-version-copy","cwd":"P:/av-kit","scope":"13 version/notice surfaces copied under scratch","phase":"targeted","exit_code":0,"result":"pass","tested_state":"read-only review of working-tree plan at supplied HEAD 8bcb4a6","output":"version-bump: 13 files written under C:/Temp/av-kit/reviewer-s57-version-copy, 0 problems after","fresh":true}
{"schema_version":"evidence.v1","check_id":"review-clean-baseline-negative","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/reviewer-clean-probe.py","cwd":"P:/av-kit","scope":"scratch git repository importing the actual clean-tree helper","phase":"targeted","exit_code":0,"result":"fail","tested_state":"current clean-tree.py on synthetic pre-existing foreign version-surface change","output":"clean-tree: 0 paths outside rows 0 to 2, exit 0; baseline-dirty allowed surface accepted: True (contract requires refusal); after version edit foreign baseline change still accepted: True","fresh":true}
{"schema_version":"evidence.v1","check_id":"review-clean-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-08-release-rc2/clean-tree.py --selftest","cwd":"P:/av-kit","scope":"scratch-only built-in cases; GIT_CONFIG_COUNT=1, GIT_CONFIG_KEY_0=commit.gpgsign, GIT_CONFIG_VALUE_0=false; PYTHONDONTWRITEBYTECODE=1","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current clean-tree helper; signing disabled only in child environment for scratch commits","output":"clean-tree selftest: 9/9 passed","fresh":true}
{"schema_version":"evidence.v1","check_id":"review-source-traces","procedure":"Read the numbered plan/task, actual audit model and cancel steps, model download adapter, builder cache-miss implementation, and RC1 Transcript wording; trace each to the invoked gate/build or row-8 fallback.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"F1 F3 F4 F5 and Q1-Q10 source inspection","phase":"targeted","exit_code":null,"result":"fail","tested_state":"working-tree plan and cited local production/dependency sources","output":"Audit model download and started cancel target are absent from the authorization table; builder cache miss calls downloadArtifactToFile; default notes reuse the held diagnosis; round-trip stdout expands home paths.","fresh":true}
```

Other executed commands: `C:/Temp/av-kit/reviewer-selftests.ps1` invoked the six named Python helper `--selftest` modes with bytecode disabled and scratch TMP/TEMP. Its first five helpers passed; clean-tree initially failed before assertions at its scratch `git commit` (exit 128). The signing-disabled rerun above passed, so that environmental failure is not a product finding. `gh release edit --help` and `gh release delete --help` both exited 0 and made no request. Targeted numbered reads and `rtk proxy rg` sweeps supplied the cited lines. The final tree observation still showed only the session plan plus the known sandbox-only ignored-file discrepancy; no repository edit was made.

## Verdict

`changes_required` — four evidence-backed High findings prevent approving this plan for execution. Correct F1–F4 through `/plan-corrections`, consider F5, and request round 2 with the complete rolling report. Mat's open D-464–D-467 decisions remain Mat's; this review does not pick their options or authorize execution/publication.


## Recheck (2026-11-08)

**Workflow**: /planning-corrections recheck
**Agent**: codex-independent-reviewer

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | open | ✅ Fixed |
| F2 | open | ✅ Fixed |
| F3 | open | ✅ Fixed |
| F4 | open | ✅ Fixed |
| F5 | open | ✅ Fixed |

### Confirmed Fixes

Paths below are relative to `P:/av-kit`. “Plan” means `docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md`; helper names refer to that same plan folder. This section supersedes round 1's open statuses and verdict. The historical report above is retained unchanged apart from its current frontmatter.

- **F1 — AUDIT_RULE / D-464: fixed.** Read the traffic table at plan:91-106 against `mcp-server/scripts/audit/fixtures.ts:7-25`, `plan.ts:568-633`, `:912-1001`, `run.ts:73-81`, the download metadata/SABR/cookies call paths, `model_manager/manager.py:74-86`, `tts/voices.py:82-85`, `tts/assets.py:45-46`, `:72-80`, and `audit-rule.py:186-201`, `:503-504`. The brief now discloses all three video metadata reads, the SABR read, C's started/cancelled download, A's completed download, the pinned ONNX weights and voice packs, vocabulary and spaCy, playlist/caption requests, and the direct proof's playlist enumeration and caption fetch. The destinations include the audit's isolated models directory. It no longer says no model is downloaded or that C never starts. Authoritative mode does not run `run.ts:555-575`'s additional container-only probes. The recommended audit rule retains its narrow block proof and explicit incomplete-verification outcome. No live request was made for this review.

- **F2 — CLEAN_TREE / D-462: fixed; mechanism `task-row-completion-predicate` closed.** `clean-tree.py:74-103` parses the baseline and identifies foreign paths still changed; `:118-123` refuses them, and `:204-211` refuses missing baseline files. The built-in selftest passed **13/13**. An independent scratch probe reproduced the original foreign `ui/package.json` case both before and after adding an rc.2 edit: both now return **1**. It also confirmed that all row-0-to-2 allowed surfaces, tests and baseline-listed plan records pass together (**0**), while a baseline rename is refused unread (**1**). The plan-folder exemption allows this session's own records; it does not exempt the foreign version surface. Plan:196 and task:54 accurately describe that behavior.

- **F3 — FRESH_BUILD / S13: fixed.** `build-rc.ps1:20-28` installs the guard before identity acquisition, output deletion or a build step. `offline-probe.ps1:14-21` reads those exact lines; its missing-block refusal is **2**, and a failed case yields **1**. Read its seven case implementations and the supplied `s57-plan-offline-probe.txt`: Node fetch and electron-builder fail at `127.0.0.1:9`, .NET HttpClient fails at that proxy, uv says the network was disabled, npm says `ENOTCACHED`, the missing NuGet package refuses, and the actual picker restore succeeds; **7/7**. The unguarded NuGet receipt has the same NU1301, as the plan explicitly acknowledges, so that diagnostic alone is not presented as proxy proof. The .NET case supplies the separate client evidence. Read the actual builder cache-miss path and proxy-agent selection (`ui/node_modules/app-builder-lib/out/util/electronGet.js:498-500`; `builder-util/out/nodeHttpExecutor.js:26-35`). These downloads now inherit the guard rather than falling back to an external fetch. The probe itself was **not rerun**, since its picker case writes into the repository and the review forbids network requests.

  Task:54 runs clean-tree selftest → clean-tree check → offline probe → build → record verification, saving each native exit before reading its receipt and stopping on failure. Clean-tree/probe failures therefore cannot proceed to output deletion. Build steps propagate their failure codes; the explicit build refusals remain 20–23. `build-identity.py:60-81` reincludes the whole build script despite excluding other docs. In scratch, changing the actual `UV_OFFLINE` guard line changed `build_inputs` and made `record_mismatches` refuse the previously matching record. Its built-in selftest also passed, including committed `--ref HEAD` equivalence. The start identity/`--expect-inputs` and later `--verify-record` flow remain intact (`build-rc.ps1:61-67`, `:102-104`; `build-identity.py:162-165`, `:201-233`).

- **F4 — RELEASE_NOTES / D-466: fixed.** Plan:118 now retains RC1's measured block and retry advice while explicitly omitting the diagnosis at `docs/releases/v0.1.0-rc.1.md:56`; the unanswered fallback selects that alternative. Executed the actual Python validation source extracted from task:59 on in-memory notes/record fixtures. For **unset** and **alternative**, notes without the diagnosis pass (**0**), and notes containing it refuse (**1**). For **recommendation** and **do-nothing**, both fixtures pass (**0**), so the check does not obstruct those explicit human choices. These are eight observed cases. The recommendation still depends on Mat's actual other-network result and requires the prose to report that result; the fixture check does not establish it. The former automatic reuse of the held diagnosis can no longer occur under the planned fallback.

- **F5 — NO_RAW_CONSOLE: fixed.** `install-roundtrip.ps1:62-66` masks the home prefix inside `Log`, before stdout, covering the updater and roaming-data calls at `:354` and `:377`. Independently extracted and executed only that masking block: plain, JSON-escaped, forward-slash and uppercase spellings all became `<HOME>` (**4/4**). No install or round-trip script run was performed. Read the supplied preconditions receipt, which now masks the path and retains the expected exits **0, 41, 40**. A fresh parser-only check of all seven plan-local PowerShell scripts reported **0 parse errors** for each. This independently establishes parsing; the unrelated parser-invocation diagnostics in the earlier home-mask receipt are not used as parsing evidence.

### Remaining Findings

#### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

None. No new finding and no open High or Critical finding.

### Affected Review Questions

- **Q1:** The prior version/installer answer stands. F2–F4 no longer prevent accepting the proposed release sequence. “With the build record committed” still requires Mat's authorized commit and successful post-commit verification in task:81; a plan approval does not establish that execution result.
- **Q4:** Now accepted. Baseline ownership is enforced without rejecting rows 0–2's own edits; missing/ambiguous baseline input refuses. The enforced build guard, seven-case supplied receipt, row-3 fail-fast order, and guard-sensitive build identity resolve the prior two exceptions. The guard being inside `build-rc.ps1` does not escape `build_inputs`.
- **Q5:** The checks/round-trip answer stands with the inaccurate installed-backend precondition removed. Plan:222 and AC-125.12 at :295 now match phase B's replacement of the scratch backend copy (`install-roundtrip.ps1:282-286`). Plan:224 accurately acknowledges the Settings readiness probe's temporary write in the nearest existing models-folder ancestor (`ui/src/main/setup-readiness.ts:102-123`). The previously stated snapshot limits remain; the plan does not claim complete content-level app-data comparison.
- **Q6:** The prior rule-shape answer stands, and its traffic-boundary exception is resolved by F1. Its fresh scratch selftest passed **46/46**. A tolerated audit remains non-pass and ends `INCOMPLETE VERIFICATION`; helper selftests do not verify Transcript end to end.
- **Q7:** Accepted with the F4 correction. D-467 A at plan:124 now explicitly saves RC1's current body, prepends the replacement line, edits through `--notes-file`, and uses `--latest=false`. The command remains Mat's after rc.2 publication. Row 8 handles each stated D-466 choice as described above. Source attachment, corrected models path and publish ordering keep their round-1 answers.
- **Q9:** Accepted. Task:65 now requires moving `s57-gate-h1.txt` and **every `s57-D6-*.txt`** into `C:/Temp/av-kit/s57/gate-run-1/` before the one unchanged rerun. These cover the fixed-name gate and per-step receipts written at `session-gate.ps1:160-164`, including the rule receipt pattern. On a W2-4 failure the later live audit has not run (`:196-200`); the second failure still requires the fix before release. Both runs are therefore retained instead of overwritten. This was verified by source inspection, without running the gate.
- **Q10:** The prior safety/value-flow answer now has its F1/F3/F5 exceptions resolved: the live audit is disclosed, the build enforces the offline boundary, and the demonstrated home-path outputs are masked. No product log change, tag/upload/publish command, or YouTube write was introduced by these fixes.

**Q2, Q3 and Q8 retain their round-1 answers without a new review.** No additional answer is inferred from unchanged code.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| F1–F5 closure and affected PR-1/4/5/8 behavior | pass | Current source traces and the concrete scratch cases above close all five failures; the changed row ordering and identity checks agree. |
| Read-only helper readiness | pass | Six helpers exit 0: red-check 38 fixtures/0 wrong; identity 0 failures; build identity passed; audit rule 46/46; status-write 0 failures; clean-tree 13/13. |
| Version dry-run readiness | pass | 13 scratch copies, 0 problems after; no repository version edit. |
| D-466 choices, baseline ownership, guard identity | pass | Independent scratch/in-memory probes all passed, including negative cases; no gate was run. |
| PowerShell syntax and home masking | pass | Seven scripts parse with 0 errors; four home-path forms masked. |
| First-run gate receipt preservation | pass | Manual trace of task:65 against gate:160-200; the archive precedes overwrite and the unchanged rerun. |
| Product Red/Green, fresh installer, packaged checks, round trip, fresh gate, live traffic | n/a | Forbidden during this review and not run. Offline-probe evidence was read from the supplied planning receipt. |
| Process paperwork | n/a | Outside Mat's requested substantive review scope. |

### Reproducible Evidence

All reviewer commands used `rtk proxy`, redirected output under `C:/Temp/av-kit`, saved the native exit immediately, read the completed receipt and propagated the saved exit. Python execution used `PYTHONDONTWRITEBYTECODE=1`; selftests and custom probes used scratch TMP/TEMP. Scratch signing was disabled solely for synthetic repositories. No repository file was edited, no prohibited secret file was opened and no network request was made.

Review observation: `git rev-parse HEAD` exited **0**, returning **8bcb4a68e796f5b340b20eae41b7ad8c71e1fab9**. No `git status`, whole-checkout identity or full tested-state derivation was run this round. `~/.config/git/ignore` was **not read** by this reviewer; `.claude/settings.local.json` was **not opened**. The host ignores that path per Mat's prompt, whereas this sandbox may expose it as untracked. The reviewer inspected the working-tree plan files on the sandbox side and does not claim an independently reconciled host/sandbox tree census.

```json
{"schema_version":"evidence.v1","check_id":"s57-r2-helper-readiness","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s57-r2-selftests.ps1","cwd":"P:/av-kit","scope":"six permitted helper selftests and scratch-only version dry run","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Working-tree plan at verified HEAD 8bcb4a6; scratch-only helper execution; ~/.config/git/ignore not read and .claude/settings.local.json not opened; host ignores that path per prompt, sandbox side not reconciled by git status","output":"red-check: 38 fixtures, 0 wrong; identity: 0 failures; build identity: passed; audit rule: 46/46; status-write: 0 failures; clean-tree: 13/13; version-bump: 13 files written under scratch, 0 problems after","fresh":true}
{"schema_version":"evidence.v1","check_id":"s57-r2-boundary-regressions","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s57-r2-targeted.py","cwd":"P:/av-kit","scope":"scratch CLEAN_TREE and BUILD_RECORD; actual row-8 Python check on in-memory inputs","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Current plan helpers imported with bytecode disabled; all git/index/blob writes in scratch; ~/.config/git/ignore not read and .claude/settings.local.json not opened; host ignores settings per prompt, sandbox status not queried","output":"Own row-0-to-2 edits accepted (0); foreign baseline version surface refused before and after rc2 edit (1,1); baseline rename refused (1); actual guard mutation changed build_inputs and record verification refused; eight D-466 option/diagnosis cases matched expected exits","fresh":true}
{"schema_version":"evidence.v1","check_id":"s57-r2-mask-and-syntax","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s57-r2-mask-parse.ps1","cwd":"P:/av-kit","scope":"parse-only inspection of seven PowerShell files; execution of extracted Log masking block only","phase":"static","exit_code":0,"result":"pass","tested_state":"Current plan-local PowerShell bytes; no build/round-trip/probe script invoked; ~/.config/git/ignore not read and .claude/settings.local.json not opened; host ignores settings per prompt, sandbox status not queried","output":"audit-clear, baseline, build-rc, install-roundtrip, offline-probe, packaged-probes, session-gate: 0 parse errors each; home mask: 4/4 forms passed; every logged fixture prefix is <HOME>","fresh":true}
{"schema_version":"evidence.v1","check_id":"s57-r2-source-recheck","procedure":"Read the changed plan/task and trace F1's audit requests, F3's guard/probe/build/identity chain, F4's fallback and F5's Log calls to current sources. Compare the supplied seven-case offline receipt with its implementation and unguarded NuGet control; compare task H1-2's archive instruction with the gate's fixed receipt names and fail-fast branch.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"F1-F5 and affected Q1,Q4,Q5,Q6,Q7,Q9,Q10","phase":"targeted","exit_code":null,"result":"pass","tested_state":"Working-tree source read at verified HEAD 8bcb4a6; supplied planning receipts observed rather than rerun; ~/.config/git/ignore not read and .claude/settings.local.json not opened; host ignores settings per prompt, sandbox status not queried","output":"Traffic inventory matches named authoritative paths; guard precedes deletion and is re-included in build_inputs; row 3 preserves failures; alternative notes omit held diagnosis; Log masks home; first-run gate receipts archive before rerun","fresh":true}
```

### Verdict

`approved` — all five round-1 findings are fixed, no new material failure was demonstrated, and the revised plan serves the registered goal. **Intent achieved: yes, as a plan.** No release execution result is certified here. D-464–D-467 remain Mat's decisions as the plan states, execution remains at the human gate, and publication remains Mat's. The coordinator owns copying this complete rolling report to its canonical path.

**Report-parser compatibility note, not a deliverable finding:** the required literal `✅ Fixed` cells above are not recognized by `tools/validate_closeout_artifacts.py:82-85`, `:551-553`, which accepts bare closure words only. The parser therefore carries four historical blocking rows despite the explicit five closures and empty current Findings table. Its parse command exits 0 and correctly identifies plan/round 2/approved, but its open-findings count is not this review's current finding count. The original report and requested closure table are preserved; no repository validator was edited and no machine approval gate was bypassed. The coordinator must reconcile that report-format compatibility before treating the parsed report state as consumable approval. The separately schema-validated v2 verdict has zero findings.

## Recheck (2026-11-08)

**Workflow**: /planning-corrections recheck
**Agent**: codex-independent-reviewer

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | fixed | fixed |
| F2 | fixed | fixed |
| F3 | fixed | fixed |
| F4 | fixed | fixed |
| F5 | fixed | fixed |

### Confirmed Fixes

- **F1: fixed.** Round 2's Confirmed Fixes F1 source-trace evidence stands; the round-3 SHA-256 comparison matches all 17 plan-folder files, including implementation-plan.md and audit-rule.py.
- **F2: fixed.** Round 2's Confirmed Fixes F2 baseline-ownership negative cases and 13/13 selftest evidence stand; the same comparison confirms clean-tree.py, implementation-plan.md and task.md are unchanged.
- **F3: fixed.** Round 2's Confirmed Fixes F3 guard, supplied seven-case receipt and guard-sensitive identity evidence stand; the same comparison confirms build-rc.ps1, offline-probe.ps1, build-identity.py and task.md are unchanged.
- **F4: fixed.** Round 2's Confirmed Fixes F4 eight in-memory fallback cases stand; the same comparison confirms implementation-plan.md and task.md are unchanged.
- **F5: fixed.** Round 2's Confirmed Fixes F5 four masking cases and parse-only evidence stand; the same comparison confirms install-roundtrip.ps1 is unchanged.

Round-3 comparison: recomputed SHA-256 for every file recursively under `P:/av-kit/docs/execution/plans/2026-11-08-release-rc2/` against `C:/Temp/av-kit/s57-plan-folder-hashes-r3.txt`: **17 files, 17 expected, 0 differences**, with no added or missing files. Every modification time matches the supplied list and precedes the round-2 dispatch end at 22:52 on 2026-11-08; the latest is task.md at 22:37:09. `rtk proxy git rev-parse HEAD` returned **8bcb4a68e796f5b340b20eae41b7ad8c71e1fab9**, exit **0**. The comparison command also exited **0**; its complete output is `C:/Temp/av-kit/s57-r3-hash-comparison.txt`.

This round carries round 2's conclusions forward and repairs only their machine-readable closure representation. The original round-2 body, including its first Recheck section and compatibility note, is preserved exactly; only current frontmatter round changes to 3. No plan review, selftest or Q1-Q10 reassessment was repeated. No network request, gate, build, installer, smoke or offline-probe execution occurred. No repository file was edited; all reviewer writes are under `C:/Temp/av-kit`. No prohibited secret file was opened. On the sandbox side, only plan-folder bytes and HEAD were checked: `~/.config/git/ignore` was not read and `.claude/settings.local.json` was not opened. Per the supplied host/sandbox distinction, that settings path is ignored on the host and appears untracked only to this reviewer; no git status or complete tested-state census is claimed.

### Remaining Findings

#### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

None. F1-F5 remain fixed; no new findings.

### Verdict

`approved` — unchanged plan bytes and HEAD support carrying round 2's approval forward. **Intent achieved: yes, as a plan.** This latest section supersedes the historical parser-compatibility note by providing bare closure words for F1-F5. Execution remains at the human gate, D-464-D-467 remain Mat's decisions, and publication remains Mat's. The coordinator saves this complete rolling report to the canonical path.
