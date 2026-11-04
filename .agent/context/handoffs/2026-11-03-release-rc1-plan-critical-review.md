---
date: "2026-11-03"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md"
verdict: "corrections_applied"
findings_count: 4
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s44-plan-2026-11-03-release-rc1"
round: 1
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

Round 2 has not run and cannot run yet. The ledger refuses it: `tokens: 9,780,882 spent + 9,780,882 reserved for the next round > budget 10,500,000`. The loop is not reset or reopened. It waits on Mat, who can lift the budget with `review_ledger.py continue` or review the plan personally (S7).

For that decision: the 9,780,882 is `input_tokens` 4,975,337 + `cached_input_tokens` 4,779,008 + `output_tokens` 26,537. `read_usage` adds cached tokens on purpose, and its docstring says `TOKEN_BUDGETS` was measured the same way, so this is the budget's unit rather than a counting bug. If `input_tokens` already includes the cached portion, which the numbers suggest but nothing here confirms, the uncached input was about 196,000.

🕐 Completed: 2026-11-03 20:47 (EST)
