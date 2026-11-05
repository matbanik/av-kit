---
date: "2026-11-04"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-04-rc2-ffmpeg-uninstall/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s49-plan-2026-11-04-rc2-ffmpeg-uninstall"
round: 1
---

# Critical Review: rc2-ffmpeg-uninstall

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

**Intent anchor:** Session 49 takes libdvdcss out of the FFmpeg av-kit ships by building FFmpeg from BtbN's recipe with the DVD scripts off and re-pinning to that build with a matching source set, makes the fetch script return its documented exit codes and makes the uninstaller remove the installer copy, with every outward step waiting on Mat.

**Intent achieved:** `yes` for plan readiness. The prescribed work delivers that objective, conditional on execution, Mat's two decisions and the separately held publication authorization. This is no claim that the untried build already works.

**Targets:** the working-tree `implementation-plan.md` and `task.md` in `docs/execution/plans/2026-11-04-rc2-ffmpeg-uninstall/`, with the named production code, tests, installed electron-builder templates, RC1 script implementations, recipe tar and planning receipts as supporting evidence.

**Review Type:** independent plan review, ledger round 1. Claude Code / Anthropic authored the plan; Codex / OpenAI did not author it. **Checklist Applied:** PR-1 through PR-9, substantive source and behavior tracing. Report formatting and other sessions' changes were not rejection criteria.

Observed `main`, HEAD `d287c55511c769d6b56920bab39d52083f7f7173`. Only scratch files under `C:/Temp/av-kit/` were written. No tests, selftests, builds, recipe programs, installers or uninstallers were run. No forbidden secret file was opened; no ledger or outward state was changed.

Final comparison confirmed both targets unchanged since the initial read and Git status unchanged. Reviewed SHA-256: implementation plan `338fa5b21e982258d01496d68e8b5acebe305215df76081595d8a4fc027f9dc1`; task `0563a6298379b2434aac088e9c78053553529aeb4fe84167ea0f611fec48f50c`. The verdict JSON validated against the repository's v2 schema (exit 0); report checks found the exact intent anchor and all ten question answers.

## Findings

No evidence-backed High or Critical finding; no blocking finding. The Findings table is empty. The implementation note under Q9 is a safe-stop test-setup mismatch, not a false-passing delivery gate or a reason to spend another plan-review round.

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| Scope, authorship and unstarted state | pass | Codex read both targets and compared Git status with the scheduled file inventory | null | Implementation rows remain unchecked; the new scripts and tools are explicitly scheduled. |
| Source-backed objective | pass | Codex looked up D-214 and D-228 by id and read the two residual build-plan sections | null | `known-issues.yaml:3899`, `:4336`; `07-distribution.md:334`, `:349`. D-214's chosen route and the retained GPL/software encoders are preserved. |
| Plan/task alignment and prerequisites | pass | Codex traced rows 0–27, H1/H2 and the listed plan-local scripts against the prose | null | Pin/source/installer order is coherent; the host and hosting decisions hold their dependent work. |
| Deferrals | pass | Codex compared Out of Scope with the residual contracts and looked up MEU-125 | null | Version, RC2 notes and release checks belong to the existing MEU-125. No required DVD-removal or uninstall behavior is silently deferred. |

Manual observations throughout this report have observer `codex-independent-reviewer` and `exit_code: null`.

### Design Review (DR): Q1–Q10

**Q1 — Delivery. Accepted.** The plan retains GPL, x264 and x265; disables all three DVD scripts; checks the actual generated text, built zip, both shipped binaries and installed payload; changes the URL/SHA and matching source set; and exercises both software encoders directly plus a product conversion. The API's missing codec selector makes those direct encoder checks appropriate (`implementation-plan.md:248–250`, `:326–338`). No required delivery is missing from the inventories. Build success and corresponding-source assembly remain execution obligations, with explicit refusal paths.

**Q2 — Recipe and guards. Accepted on static evidence.** In the tar, `generate.sh:52`, `:83`, `:173`, `:183` and `:217` test `ffbuild_enabled`. A first `return -1` is nonzero and prevents each DVD build/layer path. The dependency name `dvd` still enters the dependency walk from `scripts.d/zz-final.sh:28`; the combine loop nevertheless calls `get_output` for its scripts (`generate.sh:223–230`). Its disabled branch calls `ffbuild_unconfigure` (`:122–130`), so libdvdread/libdvdnav supply their disable flags. No surviving enabled recipe script was found to require DVD. The GPL variant still enables GPL/version3 and the final dependency set still names x264/x265.

`makeimage.sh:21–23`, `:33–57`, `:66–73` rebuilds base/target/image with QUICKBUILD unset, and passes named build contexts. `util/vars.sh:33–38` applies the registry override to every recipe image name. `download.sh:19–62` does download disabled sources, but into the private cache; it does not make them enabled image layers. Checking makeimage's exit and the exact local image before build, followed by binary/zip checks, is a real chain against the stock-image fallback. Additional ambient overrides such as FFBUILD_OUTPUT_DIR can prevent artifact creation, but the exact-one-zip check then refuses; they do not silently certify a stock result.

Both checkout insertions are in executable positions: FFmpeg after clone/before configure inside build.sh's generated shell script; crosstool-NG in the Docker RUN `&&` chain before bootstrap. The clone is not shallow. The latter hash agrees with ct-ng-config's `CT_VERSION="1.29.0.7_b1a94f6"`. Detached checkout does not break FFmpeg's `git describe` version routine. I independently reconstructed upstream tree `322b4b725d2e1a6bd52719e751ff3766de406b2c` and patched tree `889c3500c50d31f0ec4718753b077dbe74117d32` from tar data and the five insertions; every new blob abbreviation matches the measured patch. I do not claim this proves compilation. D-254's fallback requires a recorded amendment and remeasured tree, not bypassing a failed guard.

**Q3 — ABSENCE_GATE. Accepted for its stated contract.** Banner/configuration requirements prevent an unreadable or broken executable being treated as clean; flag/demuxer checks and overlapped byte scanning cover the measured stock signatures. Zip scanning includes ffplay and every other member, although av-kit ships only ffmpeg/ffprobe. Restricting the enable-flag ban to executables avoids the demonstrated HTML false positive. The source archive must retain the recipe scripts and patch while omitting the DVD dependency trees: a universal source byte ban would wrongly reject those necessary recipe files. This is a signature/structure check tied to this recipe, not proof against arbitrarily renamed, transformed or nested hostile payloads. No such bypass was identified in the prescribed producer. Stock negatives and clean-result gates are both scheduled.

**Q4 — Source set and distribution. Accepted.** `Assembly.collect` already filters `enabled_for_build` before dependency collection (`tools/assemble_ffmpeg_source.py:700–702`); `check_configuration` rejects enabled flags without an enabled recipe (`:390–410`). Feeding both from the verified patched tree gives the intended DVD omission and stock-binary rejection. Keeping upstream URL/requested commit with resolved tree in the manifest is representable by Row/manifest. `archive_tree`'s Git operations accept a tree id. Extending DOCUMENTS and the strict document/text pairing in pack publishes the patch and driver; verify already requires every declared document and manifest source count (`:890–957`). The plan schedules both changes, not merely the constants.

Publishing the zip is itself distribution; the plan correctly attaches the complete source and directions in the same release from first availability, with retention. GPLv3 6(d) was read in the pinned FFmpeg tar's `COPYING.GPLv3:275–286`. The current [GitHub CLI implementation](https://raw.githubusercontent.com/cli/cli/trunk/pkg/cmd/release/create/create.go) creates a draft when assets are supplied, uploads them, then publishes (`:463–522`), supporting the prescribed one-invocation release with zip and source. No binary-first public upload is prescribed. Direct GNU-page requests timed out; the locally preserved licence text was readable.

**Q5 — Uninstall macro. Accepted.** The compile defines include APP_INSTALLER_STORE_FILE for non-web NSIS before the uninstaller compile (`NsisTarget.js:447–463`, `:598–613`). `multiUser.nsh:12` declares installMode; its current/all branches set shell context. LogicLib/flag support is shared by the template, whose own uninstaller uses `${ifNot} ${isUpdated}`. The inserted context switch mirrors `include/installer.nsh:88–96`, so LOCALAPPDATA resolves to the current user's cache even during an all-user uninstall. The block deletes one defined installer path and removes only an empty updater directory. It does not recursively remove user data. Normal replacement passes --updated to the installed old uninstaller (`include/installUtil.nsh:202–230`); the guard preserves the cache during that path. The rc.1→rc.2 statement is correct, as both the local call chain and [electron-builder's lifecycle documentation](https://www.electron.build/docs/nsis/#custom-nsis-script) explain. The planned -WX compile is still required runtime evidence.

**Q6 — Mat's PC. Accepted with bounded protection.** Row 0 preserves the known RC1 installer before repackaging overwrites dist. S5 protects pre-existing installation/shortcut/login-item state, including StartupApproved, and refuses an unknown updater directory. The existing launch implementation calls `app.setPath('userData', appData)` for AVKIT_APP_DATA (`ui/src/main/index.ts:219–222`); the reused GUI smoke checks that redirected path. The round trip therefore isolates Electron as well as backend data. The normal roaming av-kit-ui, local av-kit and updater directories were observed present by path-existence checks only; their contents were not read.

The new deletion is deliberately the known leftover installer, not an undisclosed loss. Phase A requires RC1's leftover; B must observe the new copy after install and its absence after uninstall; C and D exercise replacement. Together these are useful negative/positive controls. I read S5 as the external pre-state gate: C/D expressly install over the script's own controlled installation. The implementation must preserve that distinction. Top-level snapshots prove the stated preservation property, not byte-for-byte contents; isolation and narrow deletion provide the preventive protection. Normal-path S5/S6 and the explicit folder checks are adequate for this authorized round trip.

**Q7 — Human gates, briefs and order. Accepted.** D-246 honestly presents an untried long local build, machine change/password, disk growth, rollback, hosted-runner tradeoff and stop-loss. Its Ubuntu install route agrees with [Docker's official instructions](https://docs.docker.com/engine/install/ubuntu/); [GitHub's official limits](https://docs.github.com/en/actions/reference/limits) confirm the six-hour hosted-job limit. D-251 explains the options, URL, public distribution/source duty, permanence and a separate advance-authorization sentence. Both briefs are sufficient to decide from and remain Mat's decisions.

After execution authorization, rows 0–12 require neither answer. Unanswered D-246 holds row 13 onward; answered D-246 with unanswered D-251 permits build verification but holds the pin work and its dependents. `[B]` decisions are distinguished from failing commands. Rows 16/17 can write the future URL while local builds use the hash-checked cached zip. Row 27 follows review, holds AC-113.35 open until authorized, then checks a fresh live fetch. Publication precedes any pin commit/push; H2-5 only drafts a commit message. Fork, recipe commit/push, release/tag/upload and Docker installation all retain Mat's words as prerequisites. RC1 state remains a separate held question. No outward write runs merely because either brief has a recommended branch.

**Q8 — Fetch exit codes. Accepted.** Replacing terminating Write-Error calls with Console.Error.WriteLine permits the explicit 2/3/4/5 exits, matching the existing exit-6 branch. Searches found no active caller requiring exit exactly 1; the RC1 build wrapper propagates arbitrary nonzero values, and the existing tests check nonzero. The replacements preserve stderr diagnostics. AC-113.5's literal ban also requires removing the existing explanatory `Write-Error` comment at `tools/fetch_ffmpeg_windows.ps1:50`; this is a trivial Green cleanup, not missing behavior. Download/permission/corrupt-zip exceptions are outside this documented-code rider.

**Q9 — What checks prove. Accepted, with one nonblocking setup correction.** No demonstrated materially false-passing gate was found. The driver, absence, assembler and installed-smoke checks have named real producers, prescribed callers and meaningful negative inputs. The packet's substring check is only a presence check; the independent execution review must read the actual commands. It is not standalone proof of correct publication.

The plan's declared-new-import Red explanation does not match the copied helper: `red-check.py.check` accepts a `declared` diagnostic, but `check_required` rejects every diagnostic whose kind is not `assertion` (`docs/execution/plans/2026-11-03-release-rc1/red-check.py:259–267`). Thus a required `test_ac_113_16_*` that raises `ImportError: cannot import name 'check_no_libdvdcss'` is recognized as declared-new and still refused by --require. The same issue affects the new driver/encoder imports in rows 10/21. This fails closed; S3 explicitly sends the coder back to test setup. Use an assertion on module/export availability before import, or explicitly reconcile the copied helper and its selftest. Preserve the behavioral expectations and Red-before-Green order. I have not run those tests or represented a synthetic receipt as a real Red.

**Q10 — Other pin consumers. Accepted.** The repository sweep found the active fetch/assembler pins, NOTICE/README advice, deps_report regex and the two test surfaces listed in the plan. The preserved upstream BUILDS_REPO remains valid provenance. The synthetic stock ZIP root and version fixtures do not fetch or require the new archive's filename. Remaining issue/grouping references describe triage or historical RC1 evidence; excluded dated execution/release history is not a live pin consumer. No omitted active consumer was found to break or retain an incorrect current-build claim.

### Plan Review (PR)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Same scope, named scripts and delivery order; Q1/Q7. |
| PR-2 Not started | pass | Product implementations unchanged; scheduled scripts absent as expected; rows unchecked. |
| PR-3 Task contract | pass | Rows name owners, deliverables, validations, dependencies and status. |
| PR-4 Validation realism | pass | Real generate/build/archive/install checks are scheduled; Q9 identifies the safe-stop Red setup correction. |
| PR-5 Source-backed planning | pass | Residual contracts, D-214/D-228, recipe and installed templates support the design. |
| PR-6 Corrections readiness | pass | Both handoffs and rolling reviews named; round 1 requires no prior correction census. |
| PR-7 Scope discipline | pass | MEU-125 owns the disclosed release/version deferrals; no missing core deliverable. |
| PR-8 Reachability and negative oracles | pass | Actual call chains and proposed negatives traced in Q2–Q6/Q9; no demonstrated material false pass. |
| PR-9 Shared predicates | pass | Named contracts resolve the build tree, asset, gate and output identities; no unresolved materially different delivery rule. |

**Post-implementation certification:** n/a. No runtime result is established by this review.

### Durable observations

```json
{"schema_version":"evidence.v1","check_id":"s49-r1-static-recipe-tree","command":"rtk proxy python -X utf8 C:/Temp/av-kit/s49-static-recipe-inspection.py","cwd":"P:/av-kit","scope":"recipe tar read as data; Git object hashes calculated without running recipe programs","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD d287c55511c769d6b56920bab39d52083f7f7173; upstream recipe tar and the plan's five insertions","output":"archive upstream tree: 322b4b725d2e1a6bd52719e751ff3766de406b2c; build.sh a97e55c -> 8c64672; Dockerfile eacbdeb -> 931b4c8; libdvdcss 664a541 -> d944212; libdvdread f642327 -> 8e9df32; libdvdnav 3986a88 -> 107332d; independent patched tree: 889c3500c50d31f0ec4718753b077dbe74117d32","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s49-r1-design-trace","procedure":"Codex read both plan files; looked up D-214/D-228; traced the archived recipe, source assembler, fetch callers, NSIS compile and replacement paths, RC1 scripts and app-data isolation; inspected supplied planning receipts and primary documentation; searched active pin consumers.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Q1–Q10 and PR-1–PR-9 plan readiness","phase":"manual","exit_code":null,"result":"pass","tested_state":"main d287c55511c769d6b56920bab39d52083f7f7173 plus the working-tree Session 49 plan","output":"No High/Critical or blocking defect found. Recipe hash and compile-context claims supported. Actual build, source assembly, macro compilation and round trips remain unrun. Required declared-new Red imports need assertion-shaped setup or an explicit helper amendment; that mismatch refuses rather than false-passes.","fresh":true}
```

## Verdict

`approved` — the plan is ready to present to Mat for execution and the two decisions. No implementation, publication, commit or Docker-install authorization is supplied by this verdict. Carry Q9's Red setup note into implementation; it does not require another plan-review round.

Residual risk: this recipe has never been built here. Docker/toolchain/dependency failures, resource use and final payload behavior remain to be measured by the prescribed execution gates. The signature checks establish the defined absence contract, and the round trip establishes behavior on this PC; neither is an unlimited provenance claim or a clean-machine release certification.
