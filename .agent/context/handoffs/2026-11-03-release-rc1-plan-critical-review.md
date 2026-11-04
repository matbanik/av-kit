---
date: "2026-11-03"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md"
verdict: "approved"
findings_count: 2
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s44-plan-2026-11-03-release-rc1"
round: 3
---

# Critical Review: release-rc1

> **Review Mode:** `plan`
> **Verdict:** `changes_required`

## Scope

**Intent anchor:** Session 44 prepares release candidate 1 of av-kit: MIT licence, the two first-run bug fixes (MEU-108, MEU-109), RC packaging and a real installer with packaged checks (MEU-110), release notes, a publish checklist and the D-101 brief, stopping before every outward step.

**Intent achieved:** partial. The plan covers the requested preparation and preserves Mat's outward-action gates, but its notice inventory, D-101 source prescription and build fingerprint need correction before they can support publication.

**Targets:** `implementation-plan.md`, `task.md`, `session-gate.ps1`, `identity.py` and `build-identity.py` in `docs/execution/plans/2026-11-03-release-rc1/`.

**Review Type:** independent plan review, ledger round 1. Claude Code/Anthropic authored the plan; Codex/OpenAI reviews it.

**Checklist Applied:** substantive PR/IR/DR checks, source tracing, primary-source licensing research and scratch-only negative probes. Formatting and process-paperwork findings excluded as requested.

**Canonical destination:** `.agent/context/handoffs/2026-11-03-release-rc1-plan-critical-review.md`; coordinator saves this report. No repository files were edited. No product suite, session gate, build, installer or uninstaller was run. No prohibited secret file was opened.

## Findings

No Critical finding. F1-F3 block approval; F4 is a non-blocking machine-state preservation observation. All findings have High confidence and concern the deliverable, not review paperwork.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | Distribution ownership does not enumerate components embedded inside native binaries. A generator can meet AC-110.5 to AC-110.7 by emitting ONNX Runtime's MIT licence while omitting its native dependencies' notices. The existing TOC includes `onnxruntime/capi/onnxruntime.dll`; its wheel separately supplies `onnxruntime/ThirdPartyNotices.txt` (343,249 bytes in RECORD), and that notice file is absent from the TOC. The proposed tests never require it. A public installer could therefore pass the stated generator checks with incomplete attribution. **Violates AC-110: LICENCE_LIST and AC-110.8.** | implementation-plan.md:131; implementation-plan.md:133; implementation-plan.md:147; .venv/Lib/site-packages/onnxruntime-1.29.0.dist-info/RECORD:11 | Keep TOC plus RECORD for outer ownership, but explicitly collect applicable embedded-component notices and all required licence files. Reconcile unowned payloads rather than ignoring them. Add a native-wheel fixture whose primary MIT licence exists but required third-party notices are missing; generation must refuse it. Verify the resulting notices in the installed payload. | open |
| F2 | High | yes | behavior | D-101 recommends attaching exact FFmpeg source plus a generated build-script manifest as the complete remedy, understating the source set. The recommended static GPL executable also incorporates libraries such as x264/x265. A repository/commit manifest is an index, not proof that their corresponding source, patches and build scripts remain accessible. Following the brief literally can leave Mat publishing an incomplete source offer after approving the recommendation. **Violates AC-110.16's sufficient Decision Brief.** | implementation-plan.md:257; implementation-plan.md:270 | Require a verified corresponding-source set covering the actual enabled native dependencies and build recipes, with equivalent access and retention under GPLv3 section 6(d). Archive it or verify and maintain the permitted external source locations. State the real preparation burden. Qualify subprocess aggregation as the architecture-based conclusion; distinguish FFmpeg's LGPL-linking checklist from the GPL rule. | open |
| F3 | High | yes | behavior | `build_inputs` omits actual build inputs. In a scratch repository, changing each of `packaging/avkit-backend.spec`, `ui/electron.vite.config.ts` and `mcp-server/scripts/bundle.ts` changed the prospective Git tree but left the fingerprint identical. The LICENSE positive control changed it. Thus a later commit can alter backend collection, compiled UI or MCP bundling while the advertised build/commit comparison still agrees with the earlier installer. `identity.py` does not repair this: its fresh D6 identity is not compared with the installer build's identity. **Violates AC-110.10 and the stated build-to-commit binding.** | build-identity.py:20; build-identity.py:56; implementation-plan.md:293 | Include all actual build configuration and bundler inputs, and compare the recorded build identity with the final release inputs. Pair that comparison with a rechecked installer SHA-256 and recorded external payload/toolchain identities. Add a negative probe for an omitted build configuration change. This need not promise byte-reproducible builds. | open |
| F4 | Medium | no | behavior | S5 checks an existing install and Run value, but `customUnInstall` also unconditionally deletes `Explorer/StartupApproved/Run/com.avkit.app`. That value can exist without a Run entry or installed app. The stated preconditions would allow deletion of pre-existing startup metadata, and the named snapshots do not explicitly cover that key. S6 detects leftovers after deletion; it does not protect existing state. | implementation-plan.md:84; implementation-plan.md:215; task.md:55; ui/build/installer.nsh:3 | Include StartupApproved in preconditions and snapshots. Also require the throwaway install directory and shortcut destinations to be absent or owned by this run before install: NSIS recursively deletes its install directory. Preserve `deleteAppDataOnUninstall: false` and omit `--delete-app-data`. | open |

## Checklist Results

### Information Retrieval (IR)

Implementation rows remain unchecked and the new build/smoke/generator scripts are explicitly scheduled; their current absence is expected. Plan/task scope and MEU order align. Source labels are present. The task-contract linter passed: 30 rows, 28 checked command cells, two view-file exemptions, acyclic dependencies. These observations establish plan readiness only, not execution results.

HEAD is `3dd591c3c671379bd0bf04e0645e12777f411673`, matching `baseline.sha`. Git status also lists untracked `.claude/settings.local.json`, in addition to the disclosed LICENSE, README, plan and images. I did not open it. S4 therefore requires coordinator resolution before execution; no deletion, stash or automatic allow-list expansion is authorized.

### Design / Documentation Review (DR)

| Question | Result | Accepted and not accepted |
|---|---|---|
| Q1: Publish preparation | partial | MIT metadata, fresh build, installer round trip, release notes, explicit publish checklist and held decisions address the request. F1-F3 prevent treating the proposed outputs as sufficient publication evidence. FFmpeg re-pin work after Mat's ruling is an explicitly acknowledged dependency, not an unauthorized omission. |
| Q2: Outward steps and host safety | partial | No row authorizes commit, push, tag, release, visibility change, re-pin or a D-101 ruling. Throwaway app data and NSIS data-preservation configuration are appropriate. The custom uninstall macro contains only the two named registry-value deletions. Silent one-click installation does not automatically launch the app unless force-run is requested. F4 limits the claim that S5/S6 protect all pre-existing host state. |
| Q3: D-101 | partial | Keeping software encoders is a sound product reason to prefer the GPL option, subject to Mat's decision and F2. The adapter recommends libx265, then libx264 when hardware fallback is unavailable. `n8.1.2` does not identify the source revision described by `n8.1.2-44-g7c533d0f86`; the notices' source reference is insufficient. A pruned binary URL alone does not prove that rebuilding from preserved source is impossible. Month-end retention is finite, not permanent. |
| Q4: READY guard | pass | Reusing the same non-stateful regex before the synchronous query preserves today's publish predicate and reduces blocking calls. `confirmReadyAndPublish` deliberately does not gate publication on the CIM result. Split READY text remains an existing stream-framing bug; the guard does not worsen it. This is residual risk, not a newly introduced defect. |
| Q5: Output parent | pass | Filesystem creation belongs in the infrastructure adapter, matching Capture's mkdir precedent. Standard mkdir OSError messages name the path; conversion's `_run_one` catches the exception and persists Failed with `str(exc)`. The planned service assertion and no-encode-spawn assertion are appropriate. |
| Q6: Licence generator | partial | TOC source paths plus RECORD can identify ordinary modules, native-wheel owners and data-only distributions. They do not enumerate embedded native components. F1 applies. The UI production closure is reasonable for the inspected imports. Electron-builder already retains Chromium notices and renames Electron's licence to `LICENSE.electron.txt`; do not falsely report them absent, but verify them in the final layout. Keep .NET notices tied to the actual published runtime. Fail closed on unknown payload ownership or missing applicable notices, as well as missing primary licences. |
| Q7: Prerelease versions | pass | Installed electron-builder maps `0.1.0-rc.1` to numeric NSIS `0.1.0.0` and channel `rc`. Python accepts `0.1.0rc1`. The OpenAPI test compares to `__version__`, not a hard-coded stable version. MCP serverInfo accepts the version string. Lock regeneration plus frozen sync is planned. Future installed-version assertions must distinguish NSIS's numeric resource from the application display version. |
| Q8: Packaged checks | partial | The checks cover a real installed backend, first conversion, MCP startup, cached offline TTS, GUI readiness and uninstall. They do not prove every packaged feature: a present picker executable with a missing sidecar DLL can pass the layout and page smoke because neither invokes Capture's real picker. Offline cached TTS also does not prove first provisioning into an empty cache. Retain these as explicit publish-checklist coverage alongside the already deferred clean-machine test; this review does not claim those paths failed. |
| Q9: Identity | fail | The D6 identity hashes broad source state and selected runtime versions; it is not an installer attestation. F3 demonstrates the incorrect build fingerprint. Ignored built outputs and the installer bytes are not covered by that Git-tree fingerprint; recording SHA-256 without rechecking the file at use time does not bind a later file. |

The licensing conclusions above use the [FFmpeg legal page](https://ffmpeg.org/legal.html), [GPLv3 sections 1, 5 and 6 reproduced by GNU GCC](https://gcc.gnu.org/onlinedocs/libgomp/Copying.html), and [BtbN's retention and variant documentation](https://raw.githubusercontent.com/BtbN/FFmpeg-Builds/master/README.md). The direct GNU licence URLs timed out; the GNU-hosted reproduction was readable. FFmpeg labels its checklist as advice for LGPL library linking. GPLv3 permits independent aggregation and external source hosting under conditions; subprocess use supports the aggregation conclusion here, rather than automatically deciding every possible integration. BtbN says month-end releases are retained for two years and 14 daily builds are kept. I could not independently retrieve the proposed retained-tag scripts; current upstream [x264 build script](https://raw.githubusercontent.com/BtbN/FFmpeg-Builds/master/scripts.d/50-x264.sh) confirms static incorporation and repository/commit pins, not the availability of the complete proposed source set.

### Post-Implementation Review (PR)

Not applicable as execution certification. The full product gate, Red/Green results, fresh installer, install/uninstall round trip and clean-machine results have not been produced by this review. The existing August build/TOC was inspected only to demonstrate an actual inventory case.

### Commands and durable observations

All commands ran from `P:/av-kit`; outputs were redirected under `C:/Temp/av-kit` and exits preserved. Scratch Git probes created no commits and did not touch the real index.

```json
{"schema_version":"evidence.v1","check_id":"s44-r1-build-and-notice-probe","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s44-review-probe.py","cwd":"P:/av-kit","scope":"build-identity negative cases and existing native-wheel inventory","phase":"static","exit_code":0,"result":"fail","tested_state":"HEAD 3dd591c; unstarted Session 44 plan; scratch-only mutations","output":"Changing packaging/avkit-backend.spec, ui/electron.vite.config.ts and mcp-server/scripts/bundle.ts each produced tree_changed=True and identity_unchanged=True; LICENSE control produced identity_changed=True. Existing TOC contains onnxruntime.dll; TOC_NOTICE_ENTRIES=[]; RECORD separately lists onnxruntime/ThirdPartyNotices.txt. Probe exit 0 means these defect demonstrations succeeded.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r1-version-probe","command":"rtk proxy node C:/Temp/av-kit/s44-review-version.cjs","cwd":"P:/av-kit","scope":"installed electron-builder version conversion","phase":"static","exit_code":0,"result":"pass","tested_state":"installed app-builder-lib with synthetic version 0.1.0-rc.1","output":"NSIS VIProductVersion: 0.1.0.0; release channel: rc","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r1-source-review","procedure":"Read the five targets and referenced production paths; trace READY matching, conversion exception propagation, NSIS deletion behavior and packaged entrypoints; compare D-101 with the primary sources linked above.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Q1-Q9 substantive plan review","phase":"manual","exit_code":null,"result":"partial","tested_state":"HEAD 3dd591c and disclosed uncommitted plan; no product execution","output":"Accepted the two fix designs, version choices and outward gates. F1-F3 remain blocking; F4 is non-blocking. StartupApproved and final payload verification require the qualifications recorded above.","fresh":true}
```

## Verdict

`changes_required` — correct F1-F3 through `/plan-corrections`, preserve the authorized scope and outward gates, then return for round 2. F4 should be incorporated before running the installer on Mat's PC. No implementation or publication approval is given.

Residual risk: this is a plan review. It establishes neither successful packaging nor clean-machine operation, source-offer completeness for a future FFmpeg pin, or the behavior of build/smoke scripts that have not yet been written.

🕐 Completed: 2026-11-03 20:02 (EST)

---

## Corrections Applied — 2026-11-03 (round 1 → round 2)

> **Corrector:** Claude Code / Anthropic (plan author, coder role). **Verdict set:** `corrections_applied`. This is not an approval: only an independent `/plan-critical-review` pass, or Mat as the named fallback (S7), can clear the plan. The reviewer's text above is unchanged.

**Plan summary:** The plan's scope and outward gates did not change. It still prepares MIT licensing, the two first-run fixes, RC packaging, a real installer with packaged checks, release notes, a publish checklist and the D-101 brief, and it stops before every outward step. The corrections change how the licence list is built, how the build is bound to the commit, what the D-101 brief claims, and what row 12 protects on Mat's PC.

### Finding dispositions

| # | Verified? | Disposition | Where (plan = `implementation-plan.md`, task = `task.md`) |
|---|---|---|---|
| F1 | Confirmed. `onnxruntime/ThirdPartyNotices.txt` (343,249 bytes) is in `RECORD` and in no TOC. numpy has the same pattern: three vendored licences inside the package. | **Fixed.** The generator now reads the shipped payload (`COLLECT-00.toc` plus `PYZ-00.toc`), takes every licence or notice file in each owner's `RECORD`, and refuses any payload with no owner outside five named classes. It also refuses a build whose TOCs disagree with `_internal` or the exe's module archive. Electron and Chromium notices are checked in the layout, not regenerated. | plan §Complete licence list, AC-110.5, .6, .8, .11, .17, .18, D-183; task row 8 |
| F2 | Confirmed by a static read of the candidate tag's scripts, never run: GPL 106 enabled scripts and 104 distinct repositories; LGPL 94 and 92; 12 GPL-only. | **Fixed.** The D-101 brief now says what complete source means, how much there is, and the three ways to provide it. It says the work is unmeasured and should be priced before committing. It adds a custom minimal build row, corrects the LGPL row (the source set barely shrinks), separates FFmpeg's LGPL checklist from the GPL rule, and marks the §5 aggregate reading as a conclusion from the architecture. The recommendation stays GPL, and the ruling stays Mat's. | plan §D-101, §Research; `C:/Temp/av-kit/rc1/d101-exact.txt` |
| F3 | Confirmed. The old allow-list fingerprint omitted real build inputs. | **Fixed.** `build-identity.py` is inverted: it hashes every tracked file outside a short exclude list. The build writes a record holding the identity, installer size and SHA-256, FFmpeg hashes, .NET runtime packs, Microsoft runtime DLL hashes and toolchain versions. `--verify-record` fails on a changed product file or installer and runs at the gate and again before the tag. A mismatch means rerunning rows 10 to 12, never editing the record (S8). | plan §Single-statement contracts `BUILD_RECORD`, §3, AC-110.19, D-184, S8; task rows 10, 13; `session-gate.ps1`; `build-identity.py` |
| F4 | Confirmed. `ui/build/installer.nsh:3` deletes the `StartupApproved\Run` value unconditionally, and NSIS deletes its install folder recursively. | **Fixed.** S5 now also refuses on a `StartupApproved\Run` value, an existing throwaway install folder, anything in `%LOCALAPPDATA%/Programs/av-kit`, or an existing `av-kit.lnk`. Snapshots cover those keys and shortcuts. `deleteAppDataOnUninstall` stays `false` and `--delete-app-data` is never passed. | plan `:84`, §4, S5, AC-110.15; task row 12 |

Verified: 4 confirmed, 0 refuted.

**Q8 residuals, also applied:** The publish checklist's clean-machine step now includes a real F2 picker capture and first model provisioning into an empty cache. The packaged check adds the picker's `.deps.json` and runtime files, plus its no-argument self-check. That check proves .NET and WinForms load, not that a capture works.

**One reviewer note not carried:** The review says `git status` lists an untracked `.claude/settings.local.json`. On this machine it is ignored (`C:\Users\Mat/.config/git/ignore:1`, `git status --ignored` shows `!!`) and does not appear in `git status --short`, so S4 is unaffected. The file was not opened.

### Other correction-pass changes (found by the corrector)

- **Module bans read the wrong place.** `tools/smoke_packaged_tts.py` only tests for folders under `_internal`. The 2026-08-24 exe holds `phonemizer` (GPLv3+), `espeakng_loader`, `misaki.espeak` and `kokoro` as pure-Python modules inside its archive, so that check would have passed it. AC-110.11's bans now read the shipped exe's module archive, and the old exe is kept as a negative control (SHA-256 `3d5691fc…4da87`). `build-rc.ps1` refuses to run without it.
- **The stale installer must never be uploaded.** `ui/dist/av-kit Setup 0.1.0.exe` predates the current spec and carries those modules. The plan says so, and `build-rc.ps1` clears `ui/dist`, `packaging/build` and `packaging/dist` first.
- **Build order.** The generator needs the picker's fresh `.deps.json`, and electron-builder needs the generator's output, so plain `npm run dist` cannot be used. §3 now lists the order step by step.
- **Runtime libraries.** A throwaway probe build of today's spec showed CPython's other native libraries are not covered by its `LICENSE.txt`. `packaging/licence-overrides/` will hold reviewed texts for OpenSSL, libffi, SQLite, xz, expat, libmpdec, zlib and HACL\*. The probe also took 47 Windows runtime DLLs from a JDK folder on `PATH`, so the build record hashes them.
- **Mat's real data.** `%LOCALAPPDATA%/av-kit` holds real data. Row 12 snapshots its top-level names only, never its contents, and S6 fails if an entry is lost.
- **Offline TTS only.** The smoke uses cached models on a copy of the backend. `smoke_packaged_tts.py --phase online` rebuilds the onedir, so it never runs after row 10.
- **A re-pin needs more than the pin.** If the D-101 ruling changes FFmpeg, the checklist now also refreshes the cached archive and updates the `## FFmpeg` section of `THIRD_PARTY_NOTICES.md`, the tests that pin the old version and the README's FFmpeg lines, before rows 10 to 12 rerun.

**Plan-local scripts changed (review targets, not production code):** `build-identity.py` rewritten; `session-gate.ps1` gains `build-identity-selftest` (static), `build-record` (full) and the scope prefix `packaging/licence-overrides/`. No file under `packages/`, `ui/`, `mcp-server/` or `tests/` changed.

### Verification

| Check | Result | Receipt |
|---|---|---|
| Task contract lint, after the last `task.md` edit | Exit 0: 30 rows, 28 fully checked, 2 exempt, dependencies acyclic | `C:/Temp/av-kit/census-s44/task-lint.txt` |
| `build-identity.py --selftest` | Exit 0, 18 checks passed, in a scratch repository | `C:/Temp/av-kit/rc1/build-identity-selftest.txt` |
| `session-gate.ps1` parser | 0 errors; parsed only, not run | Observed in this pass |
| Probe build of the current spec, throwaway folders only | `COLLECT` equals `_internal`; `PYZ-00.toc` equals the exe's 4,569 modules; banned modules absent; 69 owned distributions, none missing a notice file named in `RECORD` | `C:/Temp/av-kit/rc1/probe-scan.txt`, `pyz-real.txt` |
| Tree | `HEAD` `3dd591c`, equal to `origin/main` and `baseline.sha`; untracked paths are only `LICENSE`, `README.md`, `docs/images/`, the plan folder and this review | `git status --short` |

Nothing was built into the repository, installed, committed or pushed. No product suite ran: this pass changed plan material only. The generator, smoke and install scripts do not exist yet, so none of their behaviour is proven.

### Blast-radius census (Step 5c)

Receipts: `C:/Temp/av-kit/census-s44/<slug>-{old,new}.txt`; per-hit dispositions in `dispositions.txt`; variant sweep in `variants.txt`. Line numbers in the `-old` receipts are from before the edits. A hit is `updated` when that exact line no longer exists and `confirmed-consistent` when it does.

| Changed value (slug) | Old-value sites | Updated | Confirmed consistent |
|---|---|---|---|
| `ac-last` | 2 | 2 | 0 |
| `analysis` | 1 | 1 | 0 |
| `build-identity` | 2 | 2 | 0 |
| `build-inputs` | 0 | 0 | 0 |
| `decision-last` | 3 | 2 | 1: `id: D-182` is still valid; D-183 and D-184 follow it |
| `dist-script` | 2 | 2 | 0 |
| `extract-only` | 3 | 2 | 1: D-182's basis still holds |
| `far-smaller` | 1 | 1 | 0 |
| `fixture-toc` | 2 | 2 | 0 |
| `internal-bans` | 1 | 1 | 0 |
| `legal-html` | 4 | 3 | 1: the research link stays valid |
| `lgpl` | 2 | 2 | 0 |
| `month-end` | 2 | 2 | 0 |
| `no-gpu` | 1 | 1 | 0 |
| `one-rebuild` | 1 | 1 | 0 |
| `preconditions` | 1 | 1 | 0 |
| `prospective` | 1 | 1 | 0 |
| `repin-clause` | 1 | 1 | 0 |
| `run-key` | 2 | 2 | 0 |
| `run-value` | 3 | 3 | 0 |
| `sdk-root` | 1 | 1 | 0 |
| `source-attached` | 1 | 1 | 0 |

New-value sweeps, read in full, all consistent (16): `collect`, `pyz`, `build-record`, `BUILD_RECORD`, `ac-17`, `ac-18`, `ac-19`, `d-183`, `d-184`, `startup-approved`, `negative-control`, `licence-overrides`, `dist-prep`, `s8`, `build-identity`, `repin-clause`.

Semantic variants swept (22), with hit counts: `Analysis` 0, `TOC` 6, `tree hash` 0, `GIT_INDEX_FILE` 0, `installer.sha256` 0, `build-identity.txt` 0, `npm --prefix ui run dist` 2, `run dist` 2, `source set` 5, `manifest` 2, `no GPU` 0, `no-GPU` 0, `Run value` 0, `login item` 0, `small release` 0, `shortcuts` 2, `s32-smoke` 2, `smoke_packaged_tts` 3, `--phase` 2, `stale` 6, `THIRD_PARTY_LICENSES` 6, `phonemizer` 5. All hits are consistent; `manifest` now means package manifests only, not the removed build-script manifest.

Blast-radius census: 22 values changed, 22 variants swept, 37 sites found, 34 updated, 3 confirmed consistent.

### Round 2 status

When this section was first written, the ledger refused round 2 on its token budget. Mat then ruled: "approve tripple of the token budget and add MEU-111". The ledger's budget went from 19,000,000 to 57,000,000, which reads that as three times the figure then in force; Mat was told and can correct it. Round 2 then ran. Its report and the corrections follow.

On the units: round 1's 9,780,882 is `input_tokens` 4,975,337 + `cached_input_tokens` 4,779,008 + `output_tokens` 26,537. `read_usage` adds cached tokens on purpose, and its docstring says `TOKEN_BUDGETS` was measured the same way, so this is the budget's unit rather than a counting bug. If `input_tokens` already includes the cached portion, which the numbers suggest but nothing here confirms, the uncached input was about 196,000.

🕐 Completed: 2026-11-03 20:47 (EST)

## Recheck (2026-11-04)

**Workflow:** `/plan-critical-review`, ledger round 2  
**Agent:** Codex / OpenAI, class `avkit_independent_reviewer`  
**Author:** Claude Code / Anthropic  
**Loop:** `s44-plan-2026-11-03-release-rc1`  
**Requested verbosity:** standard  
**Verdict:** `changes_required`

### Scope

**Intent anchor:** Session 44 prepares release candidate 1 of av-kit: MIT licence, the two first-run bug fixes (MEU-108, MEU-109), RC packaging and a real installer with packaged checks (MEU-110), release notes, a publish checklist and the D-101 brief, stopping before every outward step.

**Intent achieved:** partial. The four previous findings are corrected. Two newly added audit controls can nevertheless certify missing or failed release verification.

Reviewed `implementation-plan.md`, `task.md`, `session-gate.ps1`, `identity.py`, `build-identity.py` and `audit-rule.py` under `docs/execution/plans/2026-11-03-release-rc1/`, limited to F1–F4 corrections and the changes identified since round 1. HEAD and baseline both equal `24e27354e35eccc0cfa7d7e76357e673a6e38c23`. MEU-111's inclusion is Mat's decision and accepted. Already completed repository/public/CI/dependency actions are outside this review.

This is an independent, read-only plan review. Only scratch probes, receipts and this report were written under `C:/Temp/av-kit`. No repository file, index, branch, tag, ledger or remote was changed. No prohibited secret file was opened. No product suite, full session gate, live audit, build, install or uninstall was run. The coordinator saves this section into `.agent/context/handoffs/2026-11-03-release-rc1-plan-critical-review.md`.

### Prior Pass Summary

| Finding | Prior status | Recheck result |
|---|---|---|
| F1 — incomplete embedded native notices | open / blocking | Fixed in the plan. Every owner's RECORD notice is collected, TOCs are reconciled with the payload, unknown ownership refuses, and AC-110.17 explicitly checks ONNX Runtime and numpy notices. |
| F2 — insufficient corresponding-source prescription | open / blocking | Fixed in the brief. It now covers enabled dependencies and recipes, source access and retention, and the unmeasured preparation burden. D-101 remains Mat's decision. |
| F3 — omitted build inputs | open / blocking | Fixed. The inverted fingerprint includes the named omitted configurations and new inputs by default; the record rechecks installer bytes at H1-2 and before tagging. |
| F4 — existing startup/install state | open / non-blocking | Fixed. S5 and row 12 explicitly protect StartupApproved, install destinations and shortcuts, with snapshots and preserved app data. |

### Findings

No Critical finding. Both new findings have High confidence, are blocking, and concern committable release-verification tooling rather than review paperwork.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F5 | High | yes | control-defeat | **The caption exception also tolerates a materially broken compile result.** mechanism: `environment-proof-masks-product-failure`. The real `transcript.compile` observer returns `no transcript fetched (...); ...channel_vol1.md missing` when an IP-blocked job has zero completed transcripts and compile reports a nonexistent file. `audit-rule.py` accepts the prefix and ignores that independently detected missing output. Feeding this actual observer result into a 99-step run-3 summary edited to isolate the caption failure produces `problems=[]`; the proof also passes when the independent fetch is blocked. A broken compile writer/path can therefore pass the release gate alongside a genuine IP block. The independent fetch proves the block exists, not that Transcript has no other regression. The plan nevertheless claims a transcript bug still stops the gate, and row 13 does not explicitly require the public notes/checklist to disclose incomplete Transcript verification. **Violates D-186's only-caption-failure claim, the authoritative audit's no-tolerance contract, and AC-110.16's truthful release limitations.** | `audit-rule.py:57`, `audit-rule.py:207`; `implementation-plan.md:275`, `implementation-plan.md:360`; observer `mcp-server/scripts/audit/plan.ts:1176` | Keep missing/empty/outside-root compile outputs and other independent failures non-tolerable. Treat a remaining caption-only failure as explicitly incomplete verification, reconcile any RC exception with the authoritative audit contract, and require the release notes and publish checklist to name `YOUTUBE-CAPTIONS-IP-BLOCK`, the unverified Transcript path and the acceptance/recheck condition. Do not claim the separate fetch excludes a product regression. | open |
| F6 | High | yes | control-defeat | **A failed cleanup permits a crashed audit to reuse an old summary.** mechanism: `stale-output-after-cleanup-failure`. The gate uses `$ErrorActionPreference='Continue'` and never checks that `Remove-Item` succeeded. A scratch Windows probe held the summary open for reading without delete sharing: removal reported the locked file and nonempty directory, execution continued, a stand-in Node process exited 1 without writing a summary, and the retained same-HEAD summary still passed `problems()` and the blocked-fetch condition. During uncommitted implementation HEAD stays fixed, so matching it cannot establish which inputs or run produced the summary. A new image/transport failure can consequently disappear behind a previous result, defeating the fresh live check and AC-111.4's refusal of connection loss. | `session-gate.ps1:21`, `session-gate.ps1:173`, `session-gate.ps1:203` | Make cleanup failure stop the gate and prove the old summary is absent before launch, or use a fresh run-specific output directory and consume only its summary. Add a scratch negative case for locked output followed by child exit 1; it must fail before tolerance is considered. | open |

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| Plan/task alignment and not-started state | pass | Codex read both targets and their Git diffs | null | New MEU-111 rows, version/build/release rows and gates align; task rows remain unchecked. This is readiness review, not implementation approval. |
| Baseline and scope binding | partial | `rtk proxy git rev-parse HEAD`; extracted and executed the gate's actual scope-check Python | 0 / 1 | HEAD equals baseline; actual scope check reports `head moved (S4): False`, `outside scope: ['.claude/settings.local.json']`. S4 correctly refuses that pre-existing file. It remains unopened and untouched; coordinator must resolve its ownership before execution. This is the existing round-1 stop condition, not a new finding. |
| Correction evidence | pass | Codex read correction dispositions and named selftest/probe receipts | null | F1–F4 changes are present. Supplied build selftest reports passed; identity selftest reports 0 failures. These were inspected, not rerun here. |
| Expected Python failures | pass | Codex compared row 0, gate's list and baseline changes | null | Only AC-24.10 and AC-25.10 remain eligible, intersected with actual row-0 FAILED ids. AC-25.7 is removed. Missing baseline evidence excuses nothing. Row 0 provisions Electron and built MCP outputs. No baseline suite was run by this reviewer. |

#### Design / Documentation Review (DR)

| Question | Result | Accepted and not accepted |
|---|---|---|
| Q1 — F1–F4 corrections | pass | All four hold; the new baseline and MEU-111 do not undo them. F3's original omitted-input defect is fixed, not reopened by the new audit findings. |
| Q2 — moved baseline | partial | Full SHA matches. Newly required MCP and audit paths are allowed; committed LICENSE/images no longer need an execution exception. Runtime identity still hashes the entire installed Python distribution set, so an empty NAMED_DISTRIBUTIONS does not omit updated dependencies. The new report exclusion is consistent with copying it after the gate. S4 currently refuses the pre-existing settings file as designed. |
| Q3 — authoritative tolerance and public understanding | fail | Running the live audit is appropriate after the schema/dependency change. Leaving its report non-pass and its baseline untouched is appropriate. Turning that result into `session-gate: all steps exit 0` does not establish every action works end to end. The container census is explicitly non-authoritative; copying its proof does not establish the stronger release claim. The plan needs an explicit public Transcript-verification limitation, not only an internal issue and report. F5 applies. |
| Q4 — audit-rule and stale output | fail | Supplied 18-case selftest passes independently. It does not cover F5's actual observer output or F6's cleanup failure. Both defects were demonstrated in scratch. The author's proof and this review's reduced summaries are edited run-3 data, not actual one-failure live audit runs. No clean one-failure live run is established. |
| Q5 — MEU-111 cap/message/audit change | pass | 7,800,000 raw bytes encode to 10,400,000 base64 bytes. A numeric-id JSON-RPC image response serialized by the installed SDK is 10,400,098 bytes, leaving 85,662 below its 10,485,760 limit and decoding intact. The proposed real-stdio boundary/follow-up-call tests and imported SDK-limit test are appropriate. Refusing only with `payload_too_large` and independently oversized REST bytes preserves the intended audit oracle. The message's `get` plus original/annotated path fallback is actionable. This conservative common cap can refuse images larger-buffer clients handle; it deliberately prioritizes supported SDK clients, leaves REST unchanged and makes no universal-client guarantee. Other clients and the new product behavior were not tested here. |
| Q6 — publish checklist | partial | Steps 0–9 have a workable order: D-101, any required re-pin/source preparation/rebuild, push and check CI, verify local installer against HEAD, tag, draft assets, clean-machine verification or Mat's waiver, publish, then README and repository presentation. The tag workflow is correctly identified as FFmpeg-less and upload-free, so it supplies no release asset. Row 10 removes stale outputs, and the record plus renamed installer and module-archive bans protect against uploading the old GPL-phonemizer installer. The README's existing no-installer notice stays until publication and is explicitly removed afterward. Keep source access a publication precondition under D-101. The new Transcript verification exception must be included in the public release materials under F5. No outward action is authorized by this verdict. |
| Q7 — dependencies/licence/version assumptions | pass | The post-batch receipt records 73 owners, exact COLLECT/disk and PYZ/exe agreement, no banned modules, no owner without notice, and num2words as the sole GPL-class owned distribution. D-183 inventories actual owners/versions rather than pinning 69, and still gathers the numpy/ONNX Runtime embedded notices. The version rows cover the actual package/server/OpenAPI surfaces; audit client fixture versions are not release surfaces. The changed tools/list shape is correctly a reason to run the audit. This accepts the design and supplied probe, not an independently rebuilt payload. |

All manual entries above were observed by Codex on the current six targets, relevant production paths, current workflow and provided receipts. Formatting/template checks are intentionally outside this review's findings.

The corrected source-access prescription is consistent with [GPLv3 sections 1 and 6(d), reproduced by GNU](https://gcc.gnu.org/onlinedocs/libgomp/Copying.html); [BtbN's current documentation](https://raw.githubusercontent.com/BtbN/FFmpeg-Builds/master/README.md) confirms finite monthly/daily retention and GPL/LGPL variants. The specific candidate-tag README could not be fetched in this review; candidate source counts remain the supplied static receipt's observations, not an independent source-set availability certification.

#### Post-Implementation Review (PR)

Not applicable as execution certification. No Red/Green product result, full gate, installer behavior or clean-machine result was generated here. No approval of publication, a D-101 ruling or an FFmpeg re-pin is given.

#### Commands and durable observations

All shell observations ran from `P:/av-kit` with RTK, redirected receipts and preserved exits. Probe exit 0 means the stated demonstration succeeded; it does not certify the product.

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-caption-mask","command":"rtk proxy node mcp-server/node_modules/tsx/dist/cli.mjs C:/Temp/av-kit/s44-r2-compile-probe.mts; rtk proxy python -B C:/Temp/av-kit/s44-r2-rule-probe.py","cwd":"P:/av-kit","scope":"actual transcript.compile observer and audit-rule negative case; scratch data only","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD 24e27354e35eccc0cfa7d7e76357e673a6e38c23 plus reviewed Session 44 plan revision","output":"Defect demonstration succeeded. Actual observer, with isolated-root path abbreviated: no transcript fetched (transcripts_done 0, last_item_status Failed); <isolated-root>/compiled/channel_vol1.md missing. Edited 99-step run-3 summary: summary problems []; with independently established IP block, proof problems []; missing compiled file regression tolerated True. No live audit or direct fetch executed; proof callback represents the independently blocked environment.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-stale-summary","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s44-r2-stale-probe.ps1","cwd":"P:/av-kit","scope":"gate cleanup statement with locked scratch summary and stand-in crashed Node child","phase":"static","exit_code":0,"result":"pass","tested_state":"current session-gate.ps1 cleanup/error policy; synthetic 99-step summary at current HEAD","output":"Defect demonstration succeeded. Remove-Item: process cannot access mcp-audit-summary.json because it is being used by another process; directory is not empty. continued after cleanup; stale summary exists: True. child exit: 1. stale summary problems: []; with established caption block: []. This demonstrates stale evidence eligibility; the full gate and live fetch were not executed.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-rule-selftest","command":"rtk proxy python -B docs/execution/plans/2026-11-03-release-rc1/audit-rule.py --selftest","cwd":"P:/av-kit","scope":"supplied rule selftest","phase":"static","exit_code":0,"result":"pass","tested_state":"current audit-rule.py","output":"audit-rule selftest: 18 of 18 passed. The separate negative probes demonstrate cases outside this selftest.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r2-image-envelope","procedure":"Use the installed SDK serializeMessage and ReadBuffer on a numeric-id JSON-RPC image response containing a 7,800,000-byte buffer, then decode the returned image.","observer":"Codex","cwd":"P:/av-kit","scope":"proposed image cap and installed SDK buffer arithmetic","phase":"static","exit_code":null,"result":"pass","tested_state":"installed MCP SDK and proposed 7,800,000-byte cap; no product edit","output":"raw=7800000; base64=10400000; wire=10400098; SDK max=10485760; headroom=85662; decoded=7800000. Executed Node probe exited 0; no real stdio transport or other MCP client was exercised.","fresh":true}
```

### Verdict

`changes_required` — F1–F4 are fixed; correct F5 and F6 before using the revised gate as release-readiness evidence. Preserve the existing scope, baseline and outward-action boundaries, then return through `/plan-corrections` for the next bounded review. Do not refresh the audit baseline to erase the caption regression.

Residual risk: this is plan approval work only. Packaged behavior, a clean live audit, other MCP clients, clean-machine provisioning/capture and corresponding-source availability for Mat's eventual FFmpeg choice remain unproven here. S4 also currently refuses the pre-existing untracked settings file.

🕐 Completed: 2026-11-04 00:31 (EST)

## Corrections Applied — 2026-11-04 (round 2 → round 3)

> **Corrector:** Claude Code / Anthropic (plan author, coder role). **Verdict set:** `corrections_applied`. This is not an approval: only an independent `/plan-critical-review` pass, or Mat as the named fallback (S7), can clear the plan. The reviewer's text above is unchanged.

**Plan summary:** Scope and outward gates did not change. Round 2 accepted F1 to F4, the MEU-111 cap, the dependency and licence assumptions and the checklist order. Both of its blockers were in the audit tolerance added by the previous revision (D-186), and both are corrected.

### Finding dispositions

| # | Verified? | Disposition | Where (plan = `implementation-plan.md`) |
|---|---|---|---|
| F5 | Confirmed. `plan.ts:1176` puts `no transcript fetched` in front of `fileReport`'s detail, so a missing, empty or out-of-root output carried the prefix the rule accepted. | **Fixed.** The rule now full-matches the observation: `transcripts_done 0`, status Pending or Failed, and every output in `fileReport`'s one good form with a non-zero size. It also requires reason `hollow`, which `classify.ts:40` gives only when `isError` is false, so `is_error` needs no separate check. A tolerated run now reads as incomplete verification: the gate's last line, D-186's reconciliation with "Every non-pass counts", public disclosure in AC-110.16, and new checklist step 7 for Mat's acceptance or a recheck. | `audit-rule.py`; `session-gate.ps1`; plan §Caption block rule, AC-110.16, §Release materials, D-186, D-187, S9; task rows 13, H1-2, H1-6 |
| F6 | Confirmed. The gate runs on `$ErrorActionPreference = 'Continue'`, and the cleanup line in the loop never checked that the folder went. | **Fixed.** Cleanup is now the gate step `mcp-audit-clear`, running `audit-clear.ps1`, which exits 0 only when the folder is gone. Fail-fast then stops the gate before the audit, so the rule is never reached. This keeps H1-3's fixed report path. | `audit-clear.ps1`; `session-gate.ps1`; plan §Caption block rule, scripts list, gate list, S9, check lists |
| S4 note | Not a defect. `.claude/settings.local.json` is ignored here: `git check-ignore -v` reports `C:\Users\Mat/.config/git/ignore:1`. `--exclude-standard` therefore drops it and the gate won't refuse. The reviewer's sanitized `HOME` probably hid the global ignore file. The file itself was not opened. | **No change.** | — |

### How round 2 got recorded

1. The run `s44-plan-r2` finished, but `record` refused its verdict: F5's mechanism wasn't in the closed vocabulary. F6's mechanism and its AC-111 citation would have failed next. No round was consumed.
2. The omission was the author's. The round 2 prompt named neither the vocabulary nor the citable AC set.
3. The re-issue `s44-plan-r2b` ran under the same loop id. The reviewer chose the mechanisms and citation. Comparing the two verdicts, only `mechanism` (both findings) and `violates` (F6) changed. Finding text, severity and the checklist results are identical.
4. `.agent/context/review-vocabulary.yaml` was not edited. AC-111 isn't citable in this plan loop because its AC set was read when the loop opened; the execution loop reads it fresh.
5. S7 names Mat as the fallback when the ledger refuses a round. The author used the refusal's own named relief instead, because the refusal concerned two field values and consumed nothing. Mat is told.

**Cost, which the ledger understates.** The ledger charges 9,866,049: round 1's 9,780,882 plus the re-issue's 85,167. Round 2's real run used 10,169,571 and isn't in the ledger, because the wrapper records usage only from the dispatch that recorded. Real spend is 20,035,620. No stop decision depends on the gap: after a round 3 of about 10,000,000, real spend is about 30,000,000, under the 57,000,000 budget.

### Verification

- `audit-rule.py --selftest`: 31 of 31 (`C:/Temp/av-kit/rc1/post-root/selftest-audit-rule-r3.txt`).
- `audit-clear.ps1 -Selftest`: 8 of 8 (`C:/Temp/av-kit/rc1/post-root/selftest-audit-clear-r3.txt`). Its gate cases run a copy of `session-gate.ps1` cut down to the two steps, with a child that exits 1: a held summary stops at `mcp-audit-clear` with `mcp-audit` `not_run` and no rule output; once released, the old summary is gone and the rule exits 2.
- No-traffic proof on the real record (`C:/Temp/av-kit/rc1/post-root/audit-rule-real-record.txt`): the real `transcript.compile` record satisfies `problems()`, the reviewer's missing-output form is refused, and the unreduced run-3 summary is refused.
- `build-identity.py --selftest` and `identity.py --selftest` pass. Task lint passes (`task-lint-r3.txt`, 32 rows). Both PowerShell scripts parse with 0 errors. `ruff --select I,F` passes on `audit-rule.py`. `identity.py --state-only` before this section was written is in `identity-state-r3.txt`.
- Old-address scan of the plan folder: one hit, which is H1-3's own scan pattern in `task.md`, not an address.
- **Not run:** the full gate, the live audit and the direct caption fetch. They belong to execution, and they'd add YouTube traffic. The fetch last ran before this revision, and the block held (`C:/Temp/av-kit/rc1/audit-rule-proof.txt`).

### Cross-doc sweep and census

Cross-doc sweep: 1579 files checked, 0 updated. `audit-rule` and `D-186` occur nowhere outside this plan folder, and no tool parses the gate's last line (`session-gate: all steps` elsewhere is earlier sessions' own gates and write-ups).

Blast-radius census, read in full (`C:/Temp/av-kit/census-s44-r2/`, one receipt per value; summary `C:/Temp/av-kit/census-s44-r2-summary.txt`): 17 old values with 0 hits left (`census signature`, `signature`, `gate clears`, `passes only`, `Exit 1 passes`, `checklist step 8`, `0 to 9`, `18 of 18`, the three old checklist lines and others); 16 new values with 40 hit lines, all consistent; 18 variants with 125 hit lines, all consistent. Unrelated senses of `stale`, `clear`, `publish` and `checklist` were confirmed unrelated, not changed.

Blast-radius census: 17 values changed, 18 variants swept, 165 sites found, 165 confirmed consistent, 0 old-value sites left. It ran after the edits, so it counts sites as they now stand and has no separate count of how many were updated.

🕐 Completed: 2026-11-04 01:01 (EST)

## Recheck (2026-11-04, round 3)

**Review Mode:** `plan`. **Verdict:** `approved`. **Author:** Claude Code / Anthropic. **Independent reviewer:** Codex / OpenAI; not the plan's author.

**Intent anchor:** “Session 44 prepares release candidate 1 of av-kit: MIT licence, the two first-run bug fixes (MEU-108, MEU-109), RC packaging and a real installer with packaged checks (MEU-110), release notes, a publish checklist and the D-101 brief, stopping before every outward step.”

**Intent achieved:** `yes` for plan readiness. Executing the revised plan would deliver that preparation, with the explicitly disclosed Transcript verification gap and Mat's publication decision preserved. This verdict does not certify implementation or publication readiness.

## Scope

Five review targets: `implementation-plan.md`, `task.md`, `session-gate.ps1`, `audit-rule.py`, and `audit-clear.ps1` in `docs/execution/plans/2026-11-03-release-rc1/`.

This pass covers F5/F6 corrections and “Changes since plan review round 2,” using the actual observer, classifier, record producer, relevant Transcript status/name producers, supplied corrections/census, and independent offline probes. F1–F4, the MEU-111 design, dependency/licence assumptions and the previously accepted checklist order remain accepted. No unrelated review was reopened. No finding concerns handoff formatting or process paperwork.

Observed branch `main`, HEAD `24e27354e35eccc0cfa7d7e76357e673a6e38c23`. The nine-file review input manifest has SHA-256 `c97ac8b2de9bc918e1c5e7963f16b8668747ba4246f655bd054770adfd0e301c` (`C:/Temp/av-kit/s44-r3-reviewed-state.json`). This identifies this review's files, not a full D6 runtime identity.

All reviewer writes are under `C:/Temp/av-kit/`. No repository files, ledger state, commits or outward state were changed. Forbidden secret files were not opened. YouTube requests: **zero**.

## Findings

No blocking, High or Critical findings remain. Both notes below are nonblocking corrections to substantive descriptions of the exception; neither requires another plan-review round.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F7 | Low | no | clerical | **D-186's universal regression claim is stronger than its evidence.** Confidence: High. The actual observer accepts an in-root, correctly named, nonempty file containing only `x` as the same `hollow` blocked observation, and `problems()` tolerates it. Therefore “a new regression, a bad compile output or a transcript bug still stops the gate” is not an exhaustive guarantee. This could overstate coverage for a reader of the decision log. It is nonblocking because §Verification explicitly says Transcript remains unverified, the audit stays failed, both public artifacts must disclose the gap, and Mat must accept or recheck it before publication. | `implementation-plan.md:365`; observer `mcp-server/scripts/audit/plan.ts:1176`; rule `audit-rule.py:69` | Limit the claim to the failures actually rejected: other observed non-pass steps/deltas, MCP errors, missing/empty/out-of-root outputs and unmatched observations. Keep the explicit absence of Transcript content/end-to-end proof. This does not call for widening the exception. | open |
| F8 | Low | no | clerical | **S9's first exit clause omits the tolerated-1 exception.** Confidence: High. “mcp-audit exits anything other than 0” also includes a tolerated exit 1, making the following “or it exits 1 and audit-rule.py refuses” redundant. An implementer reading S9 literally would stop unnecessarily even when the intended exception applies. It fails safely; D-186, checklist step 7 and the executable gate resolve the intended behavior unambiguously. | `implementation-plan.md:306`; actual branch `session-gate.ps1:205` | Say that audit exits outside `{0,1}` stop, and exit 1 stops unless the rule succeeds. Retain unconditional stopping on cleanup failure. | open |

Both findings have `subject: deliverable`, `finding_kind: clerical`, `mechanism: null`, and `violates: null`. They are not additional blocking control-defeat instances.

## Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1–F4 | fixed / accepted in round 2 | Acceptance retained; no changed premise identified in this revision. |
| F5 | open | Fixed |
| F6 | open | Fixed |

F5's demonstrated artifact/error bypass and false-clean result are fixed. Content verification remains expressly incomplete; F7 qualifies one overbroad sentence. For F6, an independently seeded eligible old summary cannot reach the rule when held; once released it is removed before a crashed child reaches the rule.

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| Scope and review provenance | pass | Codex read the five targets, round-2 review/corrections, supplied census summary and named receipts; checked Git HEAD/branch/status | null | Vendor-distinct reviewer; work remains unstarted in task rows. The previously observed `.claude/settings.local.json` is also visible under this sandbox's unreadable global-ignore configuration; it was not opened or changed. Existing S4 still owns that execution precondition; this is not a new correction defect. |
| Observer-to-summary trace | pass | Codex traced `simpleStep` → `transcript.compile.observe` → `stepVerdict` → `toRecord` | null | `plan.ts:194` preserves `isError`; `:1167` rejects it before the blocked observation; `classify.ts:37` produces `unexpected_error`; `run.ts:225`–`:232` records the classifier result. This simple step supplies no reason override. A genuine current-producer `hollow` record consequently implies `is_error=false`. |
| Supplied correction evidence | pass | Codex read supplied rule/cleanup selftests, real-record proof and census summary; independently reran focused checks below | null | Supplied 31/31 and 8/8 reproduced. Edited one-failure data was distinguished from the unreduced real live run, which is refused. No clean live audit is established. |

### Design Review (DR)

| Question | Result | Accepted and not accepted |
|---|---|---|
| Q1 — full-match rule and `reason` | pass | Accepted: missing, empty, outside-root, absent path, missing second volume and MCP-error outcomes from the actual observer are all refused. Pending/Failed, multiple good volumes and Unicode slugs qualify. `reason=hollow` covers `is_error` for the current producer; a hand-forged contradictory summary is not something that producer emits. Not accepted: this proves Markdown content or excludes every concurrent Transcript defect (F7). The actual `x` file case demonstrates that limit. |
| Q1 — conservative refusals | pass | `Skipped`, empty/null status and `Done` with count zero are refused; a mixed unavailable/blocked batch could therefore stop conservatively. `Done` with zero count contradicts the present REST aggregate. Semicolon-containing names are refused, but the current slugifier emits only alphanumerics and hyphens, including Unicode alphanumerics (`transcript.py:58`–`:67`), which the pattern accepts. These refusals stop the gate rather than manufacture a pass. No requirement promises tolerance of every blocked variant. |
| Q2 — what a tolerated run means | pass | Accepted: the raw audit remains non-pass and its baseline is unchanged. The real gate loop emits `INCOMPLETE VERIFICATION`, never its clean terminal marker, on simulated tolerance. H1-2's actual `Select-String` retains that marker and raw exit/rule records; H1-6 requires it in every shared handoff. “All blocking checks pass” describes the preparation gate under D-186, not a clean authoritative audit. AC-110.16 and row 13 require public disclosure and the acceptance/recheck condition. |
| Q2 — skill reconciliation | pass | D-186 honestly distinguishes continuing local preparation from changing the authoritative audit's verdict or certifying Transcript. “None. Every non-pass counts” remains true of the audit and baseline; this plan does not convert that failure to an authoritative pass. Mat's explicit prepublication decision is essential. F7 qualifies only the universal coverage sentence, not this distinction. |
| Q3 — checklist step 7 | pass | Workable after the draft and clean-machine step, before publishing. Audit exit 0 permits removing the limitation from notes and the draft. Audit exit 1 plus rule exit 0 preserves the limitation for Mat to accept or hold; it does not mean Transcript passed. Cleanup failure, refused/missing summary, or any other audit result stops. Publication is step 8, README notice removal step 9, repository presentation step 10; D-187 and row 7 agree. The real README still carries “No installer yet.” Nothing here authorizes an outward step. |
| Q4 — cleanup and fail-fast | pass | The cleanup child has `ErrorActionPreference=Stop`, verifies the output folder is gone, and runs immediately before audit in the same real step loop. The parent saves its exit before reading output and stops on failure. The supplied selftest changes the receipt root and substitutes a crashing child; it preserves the current step definitions and loop. Manual inspection confirms the real clear step and rule consume the same `$auditOut`. An independent eligible-summary test additionally proved the child is not reached while held. No stale-summary route was found in the prescribed single-session gate. |
| Q4 — state/scope/receipts | pass | The added selftest runs in static before behavioral suites and writes its copies/receipts only under C:/Temp. It does not change worktree input identity. The new `.ps1` is covered by the existing plan prefix in scope checking and is not excluded by `identity.py`'s plan-Markdown artifact exception; neither are the rule or gate scripts. The actual audit report/receipt paths remain unchanged. |
| Q5 — downstream wiring | pass | Independent scratch execution of row 13's actual Python validator returns 0 when both issue mentions exist, 1 when either is absent. This is a presence guard; semantic disclosure remains an AC/review obligation. H1-3's source remains `C:/Temp/av-kit/D6-mcp-audit/mcp-tool-audit-report.md`. H1-2/H1-6 preserve the marker. Clear precedes audit, which precedes identity-after. F8 is the remaining safe-stop wording error. |

Manual observations in these tables were made by **Codex**, on the files identified above, with `exit_code: null`. No report-format or template-order criterion was used to reject the plan.

### Post-Implementation Review (PR)

Not applicable as product execution certification. The full D6 gate, product suites, actual installer, clean-machine provisioning, live authoritative audit and direct caption fetch were **not run**. The historical caption-block proof was inspected, not refreshed. The gate-branch probe explicitly simulated its direct-fetch proof; it supplies no evidence of the current network condition.

For the correction scripts, changed paths have positive and negative assertions, no skipped cases or mocked assertion functions, and no product-code workaround. The scratch stand-ins isolate the gate's branch behavior; their simulated audit/fetch outcomes are not presented as production success.

### Commands and durable observations

The following are actual reviewer runs from `P:/av-kit`, with all-stream receipts and preserved exits. A probe exit 0 means its assertions succeeded; it does not certify release readiness.

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-rule-selftest","command":"rtk proxy python -X utf8 -B docs/execution/plans/2026-11-03-release-rc1/audit-rule.py --selftest","cwd":"P:/av-kit","scope":"current audit exception selftest; no network","phase":"static","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+review-c97ac8b2de9bc918e1c5e7963f16b8668747ba4246f655bd054770adfd0e301c","output":"audit-rule selftest: 31 of 31 passed; rejects missing/empty/outside-root outputs, wrong reasons, extra non-pass steps/deltas and failed direct-fetch proofs.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-clear-selftest","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-03-release-rc1/audit-clear.ps1 -Selftest","cwd":"P:/av-kit","scope":"current cleanup implementation and reduced copy of real gate loop","phase":"static","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+review-c97ac8b2de9bc918e1c5e7963f16b8668747ba4246f655bd054770adfd0e301c","output":"audit-clear selftest: 8 of 8 passed. Held summary: cleanup exits 1, audit not_run, no rule output. Released summary followed by crashed child: gate exits 1; rule cannot read a summary.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-real-observer","command":"rtk proxy node mcp-server/node_modules/tsx/dist/cli.mjs C:/Temp/av-kit/s44-r3-observer-probe.mts","cwd":"P:/av-kit","scope":"actual transcript.compile observer and classifier with local files and stub MCP/REST; no network","phase":"static","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+review-c97ac8b2de9bc918e1c5e7963f16b8668747ba4246f655bd054770adfd0e301c","output":"Generated 16 current-observer records. MCP-error produces unexpected_error/is_error=true. Missing output produces hollow plus full path ending missing. A file containing only x produces hollow/is_error=false and observation: no transcript fetched (transcripts_done 0, last_item_status Pending); malformed_vol1.md 1 B.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-rule-integration","command":"rtk proxy python -X utf8 -B C:/Temp/av-kit/s44-r3-rule-probe.py","cwd":"P:/av-kit","scope":"current rule against 16 actual-observer records and edited/unreduced historical summaries; no fetch","phase":"static","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+review-c97ac8b2de9bc918e1c5e7963f16b8668747ba4246f655bd054770adfd0e301c","output":"16 of 16 matched expected decisions. Missing, empty, outside, no-paths, empty-path, second-missing, MCP-error, Skipped, Done-with-zero-count, null-status and semicolon-name refused. Pending, Failed, two-volumes and Unicode slug tolerated. Malformed nonempty content also tolerated, demonstrating the disclosed content-verification limit. Real compile record accepted only in edited one-failure summary; unreduced historical run refused.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-gate-integration","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s44-r3-gate-probe.ps1","cwd":"P:/av-kit","scope":"copied real gate loop; eligible old summary; simulated audit and direct-fetch proof","phase":"static","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+review-c97ac8b2de9bc918e1c5e7963f16b8668747ba4246f655bd054770adfd0e301c","output":"6 of 6 passed. Control old summary qualifies with simulated block. Held eligible summary: gate exit 1, child not reached, audit not_run, rule not reached. Released stale summary: removed, crashed child reached, rule exit 2, gate exit 1. Audit exit 0 gives clean marker only. Fresh tolerated audit gives INCOMPLETE VERIFICATION only. H1-2 Select-String preserves incomplete marker. Zero YouTube requests.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s44-r3-plan-wiring","command":"rtk proxy python -X utf8 -B C:/Temp/av-kit/s44-r3-plan-probe.py","cwd":"P:/av-kit","scope":"changed stage/scope/identity wiring and actual row-13 validator on scratch release documents","phase":"static","exit_code":0,"result":"pass","tested_state":"24e27354e35eccc0cfa7d7e76357e673a6e38c23+review-c97ac8b2de9bc918e1c5e7963f16b8668747ba4246f655bd054770adfd0e301c","output":"Static selftest precedes full suites; clear immediately precedes audit; identity-after retained; old inline cleanup absent. Gate/rule/cleanup scripts remain bound and allowed. Row 13 both disclosures present exit 0; notes disclosure absent exit 1; checklist disclosure absent exit 1. H1-3 fixed report path and H1-6 shared marker retained. Presence validation does not substitute for semantic review.","fresh":true}
```

## Verdict

`approved` — F5/F6's blocking defects are corrected. The revised plan can prepare RC1 while honestly retaining incomplete Transcript verification and stopping before the outward steps. F7/F8 are nonblocking precision corrections; do not spend another review round on them. The cap did not alter the materiality judgment.

This approval leaves Mat's commit/push/tag/release/visibility, FFmpeg re-pin and D-101 gates intact. At checklist step 7, a tolerated audit still requires the disclosed limitation and Mat's actual acceptance or a successful recheck. No clean audit, current caption block, fully verified Transcript, corresponding-source availability or clean-machine result is certified by this review.

Report checks: durable evidence validation passed; the review validator recognized round 3 of 3, `approved`, with **0 open blocking findings** (the two open notes explicitly say `Blocking: no`). The ledger and canonical handoff remain for the coordinator to save/record without rewriting this verdict. The canonical destination is `.agent/context/handoffs/2026-11-03-release-rc1-plan-critical-review.md`; retain its earlier rounds and append this body under the round-3 `## Recheck` heading.

🕐 Completed: 2026-11-04 01:12 (EST)

## Coordinator Note — 2026-11-04 (after round 3)

> **Written by:** Claude Code / Anthropic (plan author). This note records what happened after the verdict. It does not change the verdict or the reviewer's text above.

**F7 and F8 are applied without another round,** as the reviewer directed. Both are wording only; no behaviour, rule or gate step changed. The plan's §Execution Correction Notes (ECN-1) lists each edit.

- **F7:** D-186 no longer claims a bad compile output or a transcript bug always stops the gate. It names the failures the rule does refuse and says the rule can't judge a non-empty file's content. The same overstatement ("real" output) is also corrected in D-186's decision, §Caption block rule, the round 2 change note, the rule's docstring and the gate's header comment.
- **F8:** S9 now says `mcp-audit` exits outside {0,1}, or exits 1 and the rule refuses. The cleanup clause is unchanged.

**Cost.** The ledger charges 19,098,512 of 57,000,000: rounds 1, 2 and 3 at 9,780,882, 85,167 and 9,232,463. Real spend is 29,268,083, because round 2's first run (10,169,571) finished but couldn't be recorded, and the wrapper records usage only from the dispatch that recorded. No stop decision depends on the gap.

**Validator on this rolling file.** `--review-state-only` reads round 3 of 3, `approved`. `--approved-state-only` on this file refuses with 3 open findings (receipt `C:/Temp/av-kit/rc1/post-root/review-approved-r3.txt`). Those are round 1's F1, F2 and F3, carried because the parser closes a finding only on a `Recheck result` cell that is a bare closure word with the finding's whole id: round 2's cells read "Fixed…" followed by prose, and round 3's row reads `F1–F4`. The reviewer's own text says they are fixed and accepted, F5 and F6 close normally, the reviewer's standalone report passes the same check with 0 open findings, and the ledger records approved with no blocking findings. That text is left as written; rewriting a reviewer's cells to satisfy the parser isn't the coordinator's to do. No workflow, skill or plan gate runs this check on a plan review. Rows H1-7a and H1-7b do run it on the execution review, so that prompt must ask for one row per finding id with a bare closure word.

**Loop state.** Rounds 3 of 3, approved with no blocking findings. The ledger refuses a further round unless a named human continues it, and none is needed.

🕐 Completed: 2026-11-04 01:17 (EST)
