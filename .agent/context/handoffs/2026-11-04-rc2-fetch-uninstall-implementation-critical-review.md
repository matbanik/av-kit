---
date: "2026-11-05"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s49-execution-2026-11-04-rc2-fetch-uninstall"
round: 1
intent_achieved: "yes"
---

# Critical Review: 2026-11-04-rc2-fetch-uninstall

> **Review Mode**: execution, multi-MEU / multi-handoff (MEU-113 and MEU-114)
> **Verdict**: approved

## Intent Anchor

Session 49 makes the fetch script return its documented exit codes and makes the uninstaller remove the installer copy, with every outward step waiting on Mat.

Intent achieved: **yes**, within the approved local/repackaged verification scope. This approval authorizes neither publication nor any other outward step.

## Scope

**Target**: both Session 49 MEU handoffs; the correlated implementation-plan.md and task.md; plan-local baseline, identity, Red checker, repackage, round-trip, decision-extract and gate scripts; the four product/test changes; the distribution spec, MEU SSOT/rendered state, issue register/render and triage output. Working-tree changes were compared with HEAD `83229ea69b563a03d5c47d4678619c8da4c937d8`.

**Review Type**: independent execution review, round 1 of 6. Claude Code / Anthropic authored the implementation. This reviewer is Codex / OpenAI, class `avkit_independent_reviewer`, and did not write it. Both handoffs belong to the same two-MEU plan and share its gate.

**Checklist Applied**: implementation IR-1 through IR-7 where applicable, substantive DR checks, AV-1 through AV-6, and the five questions in the dispatch. H1-7 onward and H2 remain coordinator work after this review; no missing reflection/metrics finding is asserted. Unrelated dirty files, the parked FFmpeg plan, D-266, D-268 and D-272 were treated as the supplied boundaries.

Only temporary probes, receipts and this report were written, under `C:/Temp/av-kit`. No repository file was edited. No full gate, build, repackaging, installer, uninstaller or YouTube operation was run by this reviewer. Prohibited secret locations and real application-data contents were not opened.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No findings. No evidence-backed High/Critical defect was established.

**Summary correction, non-blocking and clerical:** `.agent/context/handoffs/2026-11-04-rc2-fetch-uninstall-MEU-114-handoff.md:39` says the old cached copy was deleted before phase A. The current script and saved A-before/A-after snapshots show it remained through A and was removed by B's new uninstaller. Replace that chronology; the recorded negative control and cleanup result remain valid. The limitations section is otherwise accurate for the declared scope.

## Checklist Results

### Information Retrieval (IR)

Manual observations below were performed by `codex-independent-reviewer`; their exits are null. Command exits refer to the actual child, preserved before reading its receipt.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| Intent, author independence and complete project scope | pass | Manual: read the dispatch, plan, task, both handoffs and all claimed changes | null | Correct two-MEU target; vendor-distinct reviewer; no plan or human gate reinterpreted |
| Every primary AC appears in its owning handoff | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s49-review-audit.py` | 0 | Exact AC sub-id comparison: 14/14, comprising five AC-113 and nine AC-114 criteria |
| Fresh full-gate inputs | pass | Same audit, plus manual comparison of gate and per-step receipts | 0 | Historical identity reproduced exactly after explaining one sandbox-visible local settings path; full suite counts match |
| Source labels, exclusions and lifecycle coverage | pass | Manual: trace each AC to its Local Canon/Human-approved basis, implementation and unit/integration evidence | null | Integration ACs use real NSIS compilation and actual install/launch/uninstall receipts; MEU-125 owns the clean rc.2 repetition |
| Later reflection, metrics and final status transition | n/a | Coordinator closeout after independent approval | null | Both MEUs correctly remain ready_for_review during this review |

### Design Review (DR)

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| Fetch contracts and caller compatibility | pass | Manual: inspect script, complete test file and callers; run targeted Python tests and seven additional fixture probes | null | All explicit refusal bodies reach their documented exits; no caller branching on legacy exit 1 found |
| NSIS cleanup scope and upgrade guard | pass | Manual: compare `installer.nsh` with electron-builder's installed template, defines and upgrade arguments | null | Exact installer-copy delete; non-recursive folder removal; not-updated guard; per-machine context restored after only those two operations |
| NSIS compiler and round-trip evidence | pass | Manual: inspect repackage command, builder implementation, A-D script/receipts and saved snapshots | null | Real NSIS success under default -WX; old copy remains after A, absent with folder after B-D; launches and process cleanup pass |
| Status and issue truth | pass | Audit command above; independent MEU and issue render checks | 0 | Only MEU-113/114 change semantically; ready_for_review; two issues resolved in tree; FFmpeg issue open; decision extract equal |
| Outward-action boundary | pass | Manual: inspect actual row wrappers, plan-local scripts, baseline/current HEAD and installer hashes | null | No main-repository commit/push/tag/release/upload command in the executed rows; --publish never; local RC1 installer unchanged |

### Post-Implementation Review (PR)

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| Independent targeted Python | pass | `rtk proxy .venv/Scripts/python.exe -B -m pytest -p no:cacheprovider --basetemp C:/Temp/av-kit/rc2/tmp/s49-reviewer-pytest tests/unit/test_packaging_installer.py` | 0 | 20 passed in 3.56s; TMP/TEMP under the required rc2/tmp directory |
| Independent targeted UI | pass | `rtk proxy npx vitest run tests/unit/login-item-nsh.test.ts` from `P:/av-kit/ui` | 0 | One file, four tests passed |
| Independent refusal/boundary probes | pass | `rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s49-review-fetch-probe.py` | 0 | Seven passed: whitespace URL, short SHA, missing ffprobe, empty zip, ffprobe stub, missing licence and 1025-byte success; all ExtractOnly |
| Independent rendered state | pass | `rtk proxy .venv/Scripts/python.exe -B tools/meu_status.py render --check` | 0 | 126 MEUs, 12 phases; generated regions match |
| Independent issue render | pass | `rtk proxy .venv/Scripts/python.exe -B tools/issue_triage.py render --check` | 0 | known-issues.md is up-to-date |
| Red-to-Green proof and assertion integrity | pass | Manual: read both raw Red receipts, saved child exits and Green results; audit all tests in both changed files | null | Python nine decisive failures to 20 passes; UI two decisive failures to four passes; no new skip/only/xfail or weakened expected code |
| Handoff full evidence consistency | pass | Manual: compare both successful durable_evidence.py --require-full checks with their actual commands and independently reproduced expected state | null | Both reported OK: durable evidence records; this validates records and binding, not a fresh full execution |

### Q1 — MEU-113: documented refusal codes

Accepted. `tools/fetch_ffmpeg_windows.ps1:12` sets Stop; the six changed refusal messages now use `[Console]::Error.WriteLine`, which does not throw through PowerShell's error cmdlet. Their subsequent exits are unchanged: URL/SHA/archive absence 2, hash mismatch 3, missing binary 4, stub 5. The licence refusal still returns 6; success still returns 0. No explicit refusal body in the delivered script retains the original error-cmdlet interruption or falls through to success.

The two earlier tests now assert 2 and 3 (`tests/unit/test_packaging_installer.py:136`, `:156`). AC-113.1's three cases and AC-113.2 through AC-113.4 run real pwsh subprocesses and assert exact exit codes and diagnostic stderr (`:322`, `:336`, `:344`, `:352`). AC-113.5 (`:366`) directly enforces its literal no-Write-Error contract. The Red receipt shows `assert 1 == 2/3/4/5` with the corresponding terminating error at all six old sites; the ninth failure is the literal no-Write-Error assertion. It is not an import/setup failure. The saved child exit is 1, while the Red-check wrapper's success means it recognized those expected failures.

Additional independent cases cover the opposite missing binary, ffprobe's stub branch and the 1024/1025 size boundary. No network request was made. Caller searches across CI, tools, UI scripts/package commands and tests reveal pin readers and subprocess tests, with no caller depending on precisely exit 1. Operational filesystem/network/unzip exceptions retain their previous behavior; this session changes the explicit documented refusal exits, not general I/O error classification or archive-selection semantics.

### Q2 — MEU-114: macro and pins

Accepted. `ui/build/installer.nsh:4` guards cleanup with not-isUpdated; `:8` deletes only the template-defined installer copy; `:9` uses a non-recursive RMDir on the updater directory. Extra files prevent that directory removal. The per-machine branches (`:5`, `:10`) switch to the current user's context for these two lines and restore all-users context. The two existing registry deletions stay outside that switch and unchanged. The new block names no real av-kit application-data folder.

This mirrors `ui/node_modules/app-builder-lib/templates/nsis/include/installer.nsh:88`; `NsisTarget.js:612` defines the stored file using the updater-cache name and installer filename. `installUtil.nsh:205` passes --updated to the old uninstaller on ordinary upgrades. The macro therefore skips the intended update path.

The tests strip comments, isolate customUnInstall and track nested guard depth. AC-114.1 fails when the guarded delete/removal disappear; AC-114.2 asserts the exact package-derived directory and complete RMDir list; AC-114.3 rejects recursive removal and extra registry deletions, while AC-61.18 checks the two registry targets and include wiring. These are substantive structural pins, supplemented by compilation and runtime cleanup. They do not simulate all NSIS control flow or exercise the all-users branch.

### Q3 — MEU-114: compilation and real lifecycle

Accepted within D-268. `repackage.ps1` invokes electron-builder with `--prepackaged dist/win-unpacked --publish never`, sends output outside ui/dist, and checks RC1's original installer afterwards. Its receipt records electron-builder 26.18.0, NSIS x64, perMachine=false and exit 0. The installed `NsisTarget.js:623` adds -WX unless warningsAsErrors is explicitly false; the actual configuration has no such override. The same defines flow into uninstaller compilation (`NsisTarget.js:461`). This is evidence of real macro compilation, not a text-only pin.

The original and kept RC1 installers both independently hash to `beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7`. The repackaged installer independently hashes to `5d44f65ee37b8577ac5126bfdfe1e79bfa7db168fed7c210a7e01b489d63f7cd`, the same value seen in the runtime receipt.

| AC / phase | Accepted evidence |
|---|---|
| AC-114.5 / A | RC1 installs and uninstalls with exit 0; installer copy remains with RC1's hash; the dedicated negative-control predicate observes it |
| AC-114.6 / B | New copy exists after installation; packaged smoke passes; uninstaller finishes; both copy and updater folder are absent |
| AC-114.7 / B | Roaming av-kit-ui exists before the run and survives; all seven recorded top-level local av-kit entries are identical before/after |
| AC-114.8 / C | RC1 then new install both exit 0; new copy hash appears; packaged smoke passes; no surviving installed processes, install folder, app registration or cached copy remains |
| AC-114.9 / D | New installer runs twice, copy remains after the second install; packaged smoke passes; final uninstall is clean |

All saved A-D snapshots were parsed independently. Each phase preserves the same seven local app-data names and the roaming folder; updater entries number one after A and zero after B-D. Smoke JSON reports isPackaged=true, isolated userData, backend HTTP 200, ffmpegAvailable=true, no page errors and closed=true. The uninstaller script waits for observed cleanup rather than trusting only the first NSIS process's exit; no waiting condition remained at the deadline. The final receipt reads `install-roundtrip: exit 0`.

The declaration of limits is accepted: this is a repackaged RC1 application, version 0.1.0-rc.1, on one per-user machine; it is not the clean rc.2 build or a per-machine runtime test. Phase D cannot directly prove the intermediate skip, because installation rewrites the copy afterwards; source/pin review covers that condition. Data preservation proves top-level names and folder existence, not equality of real data-file contents. The small chronology correction above does not change those observations.

### Q4 — records

Accepted. Parsed HEAD/current comparison of `.agent/context/meu-status.yaml` finds only MEU-113 and MEU-114 semantically changed. All other top-level values and MEU-115 through MEU-126 compare equal; wrapping/quoting changes do not alter those tasks. Both delivered MEUs are ready_for_review, point to this plan and render consistently into BUILD_PLAN and the registry. The distribution notes accurately distinguish this local proof from MEU-125's later full build.

The two issue resolutions say fixed in the tree, ships in rc.2 and are supported by their behavioral evidence. FFMPEG-LIBDVDCSS-BUNDLED remains open. D-272's saved extract equals the current register's complete decision logs: uninstall D-228; FFmpeg D-214, D-215, D-266 and D-275. No tooling repair or FFmpeg/notices change is required here.

### Q5 — gate freshness, coverage and outward boundary

Accepted. Gate-before and gate-after both record:

`83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec`

The reviewer's raw identity first produced digest `1f287897784205eb60c4faa65d9e6eeb3eebf14b12a0914a4593c1834c9e916d`. Git also reported access denied for its global ignore file, making `.claude/settings.local.json` visible as one extra untracked path in this sandbox. Recomputing with exactly that path excluded, without changing repository files, reproduces the historical state above. Runtime/distribution, Node/Electron/Playwright, font and lock hashes match. This accounts for the discrepancy; it is not evidence of product drift. No secret content was needed for that diagnostic.

The full gate's per-step receipts match the handoffs: Python 1193 passed in 110.41s; UI 108 files / 1141 passed; types/lint, task-contract, scope, Red checker, UI build and state render pass; baseline-excused failures are empty. The gate ends `session-gate: all steps exit 0`. Its declared MCP/OpenAPI/Electron-E2E/build-record skips match this plan; packaged Electron was exercised in B-D. No full gate was rerun merely to reproduce the totals.

All 14 primary ACs have implementation and an applicable failure-detecting check. AC-24/25/61/110 regression families are retained; no required behavior was silently deferred. H1/H2 review/closeout rows are legitimately later. The actual row scripts contain no commit/push/tag/release/upload operation on av-kit. The identity selftest makes only its isolated scratch-fixture commit. HEAD remains the baseline; repackaging used --publish never; the original RC1 installer hash is unchanged. No evidence indicates a change to RC1's published state. This review did not query or independently certify the remote release's current state.

### Assertion-strength audit

Every test in the two changed files was inspected. Grouped rows below enumerate all tests; ratings describe what each check actually proves.

| Tests | Rating | Reason |
|---|---|---|
| test_nsis_target; test_extra_resources_from_dir; test_nsis_keep_appdata; test_no_torch_in_builder | Adequate | Existing declarative configuration checks; narrower than a compiled installer. Actual compilation/lifecycle evidence supplements them |
| test_resources_backend_vitest_scheduled; test_mcp_copy_default_vitest_scheduled | Adequate | Existing source/scheduling pins only; no new API or MCP implementation is claimed from them |
| test_mcp_snippet_keys | Adequate | Explicit required/forbidden keys for the documented snippet contract |
| test_nsis_pack_check_script | Adequate | Script fail-closed markers and real vendored binary presence/size; not an independent NSIS build |
| test_fetch_ffmpeg_rejects_blank_sha; test_fetch_ffmpeg_rejects_sha_mismatch | Strong | Tightened real-subprocess exact exit assertions and rejection of a success marker |
| test_ac_72_7_third_party_notices | Strong | Checks component-specific licence/source content and installed licence text |
| test_ac_72_7_fetch_ffmpeg_requires_license_txt; test_ac_72_7_fetch_ffmpeg_copies_license_txt | Strong | Real negative/positive subprocesses, exact exits and actual output artifacts |
| test_ac_113_1_fetch_exits_2_with_message_on_stderr (three cases); test_ac_113_2_fetch_exits_3_on_sha_mismatch; test_ac_113_3_fetch_exits_4_without_both_binaries; test_ac_113_4_fetch_exits_5_on_stub_binary | Strong | Each fixture reaches its intended refusal and checks exact process exit plus stderr |
| test_ac_113_5_fetch_script_has_no_write_error | Strong for its literal AC | Direct complete-file absence assertion |
| AC-61.18 NSH_FILE | Adequate | Executable-line targets/counts and include value, with a comment-only negative fixture |
| AC-114.1; AC-114.2; AC-114.3 | Adequate | Executable macro scope, guarded operations, exact directory and non-recursion pins; compiler/lifecycle checks supply runtime proof |

AV-1 through AV-6 pass for the changed behavior: decisive Red/Green evidence, no assertion bypass, explicit behavioral assertions, no introduced skip masking, no unfinished product placeholder and source-backed criteria. Runtime/integration checks are real receipts, not mocked unit substitutes. API error mapping, database persistence and REST/MCP boundary DTO checks are n/a because no such surface changes.

### Durable reviewer evidence

```json
{"schema_version":"evidence.v1","check_id":"s49-review-python","command":"rtk proxy .venv/Scripts/python.exe -B -m pytest -p no:cacheprovider --basetemp C:/Temp/av-kit/rc2/tmp/s49-reviewer-pytest tests/unit/test_packaging_installer.py","cwd":"P:/av-kit","scope":"Complete changed Python test file; TMP/TEMP=C:/Temp/av-kit/rc2/tmp","phase":"targeted","exit_code":0,"result":"pass","tested_state":"83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec","output":"collected 20 items; 20 passed in 3.56s. Initial default pytest temp lookup failed with WinError 5 on the existing pytest-of-Mat directory; the successful run used the isolated basetemp shown here. No product defect inferred from that sandbox error."}
```

```json
{"schema_version":"evidence.v1","check_id":"s49-review-ui","command":"rtk proxy npx vitest run tests/unit/login-item-nsh.test.ts","cwd":"P:/av-kit/ui","scope":"AC-61.18 and AC-114.1 to AC-114.3","phase":"targeted","exit_code":0,"result":"pass","tested_state":"83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec","output":"Test Files 1 passed (1); Tests 4 passed (4)."}
```

```json
{"schema_version":"evidence.v1","check_id":"s49-review-fetch-boundaries","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s49-review-fetch-probe.py","cwd":"P:/av-kit","scope":"Independent local ExtractOnly fixtures, including the opposite missing/stub binary and success boundary","phase":"targeted","exit_code":0,"result":"pass","tested_state":"83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec","output":"whitespace-url exit=2; short-sha exit=2; missing-ffprobe exit=4; empty-zip exit=4; stub-ffprobe exit=5; missing-license exit=6; valid-1025-boundary exit=0. All messages matched. Seven passed; no network requests."}
```

```json
{"schema_version":"evidence.v1","check_id":"s49-review-state-and-records","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s49-review-audit.py","cwd":"P:/av-kit","scope":"Read-only normalized identity, semantic MEU/status comparisons, exact AC coverage, decision extract, saved snapshots and installer hashes","phase":"targeted","exit_code":0,"result":"pass","tested_state":"83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec","output":"Exact gate identity reproduced excluding only sandbox-visible .claude/settings.local.json; semantically changed MEUs ['MEU-113','MEU-114']; both ready_for_review; other top-level MEU values identical. Issues resolved/resolved/open. Primary AC table coverage 14/14. Extract decision logs equal: D-228 and D-214/D-215/D-266/D-275. A-D app_data equal, seven entries; roaming retained. Updater after A has one entry, after B-D zero. Original and kept RC1 hashes beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7; new installer 5d44f65ee37b8577ac5126bfdfe1e79bfa7db168fed7c210a7e01b489d63f7cd; all assertions passed."}
```

```json
{"schema_version":"evidence.v1","check_id":"s49-review-recorded-gate-and-runtime","procedure":"Codex read the complete Session 49 gate, individual step summaries, Red/Green receipts, repackage receipt, A-D round-trip receipt and saved snapshot JSON; compared them with the two handoffs, actual scripts and current input identity. No build/install/full gate was executed by the reviewer.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Recorded full gate and compiled/installed lifecycle evidence, with declared verification limits","phase":"review","exit_code":null,"result":"pass","tested_state":"83229ea69b563a03d5c47d4678619c8da4c937d8+f7dcdeb0897c701333a4d083e689326190f9a902f14ef832e2f4ba1ed6f660ec","output":"Gate before/after equal current normalized state; every registered step exit 0; Python 1193 passed, UI 108 files/1141 passed; baseline failures excused none; session-gate: all steps exit 0. Repackage electron-builder exit=0. A retains RC1 installer copy; B-D remove copy and folder; three packaged-app-smoke passes, no surviving installed processes, data names preserved; install-roundtrip: exit 0."}
```

## Verdict

`approved` — intent achieved, with no blocking findings. Both requested fixes have meaningful failure-detecting checks and matching local execution evidence. Retain the stated limitations and make the small chronology correction when the coordinator updates its own handoff. Continue only the already authorized coordinator closeout; commits, pushes, tags, releases, uploads and any change to RC1 still wait for Mat's explicit words.

Report delivered at `C:/Temp/av-kit/dispatch/s49-exec-review-report.md`. The coordinator can copy it unedited to `.agent/context/handoffs/2026-11-04-rc2-fetch-uninstall-implementation-critical-review.md`.

🕐 Completed: 2026-11-05 15:22 (EST)
