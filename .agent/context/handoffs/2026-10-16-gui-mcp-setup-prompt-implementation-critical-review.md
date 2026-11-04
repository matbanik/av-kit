---
date: "2026-10-17"
review_mode: execution
target_plan: P:/av-kit-wt/s31b-gui-mcp-setup-prompt/docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md
verdict: approved
findings_count: 0
round: 2
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-16-gui-mcp-setup-prompt

> **Review Mode:** execution  
> **Verdict:** changes_required  
> **Intent achieved:** partial  
> **Loop:** s31b-exec-2026-10-16-gui-mcp-setup-prompt, round 1 of 6

## Intent Anchor

Session 31b delivers MEU-71 (a per-client MCP setup prompt that the Settings MCP card shows and copies, with no token in any block and a fixed `mcp-server` entry guard) and, under grouping D-56, MEU-92 (a self-contained `esbuild` bundle of the MCP server that the packaged app ships and `MCP_ENTRY_PROBE` proves starts from a built `win-unpacked` tree).

Most of this intent is delivered and supported by the recorded runs. One supported client layout can be edited without its required backup: the Claude Desktop MSIX destination and the backup destination disagree.

## Scope

**Checkout:** P:/av-kit-wt/s31b-gui-mcp-setup-prompt, branch `claude/s31b-gui-mcp-setup-prompt`, HEAD/baseline `6097cf59adc7835fa6062c8bd3d55c679aef4543`. All commands used this working directory. No plan, product or test file was read from P:/av-kit.

**Correlated handoff set:**

- `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff.md`
- `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-92-handoff.md`

Reviewed the approved contract, task/Row Evidence, complete walkthrough, both result JSON files, plan-local verifier and shell procedures, current working-tree changes and new files, relevant build-plan/SSOT changes, fixtures, compiled bundle/resource listing and the named execution receipts. REVIEW-TEMPLATE v2.2 supplied the structure; the Session 39 implementation review supplied layout calibration only.

Claude Code/Anthropic authored the implementation. This Codex/OpenAI reviewer authored none of it. No repository file was written. Only this report and scratch command receipts were written under C:/Temp/av-kit. The dispatcher owns the verbatim copy to `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-implementation-critical-review.md`.

**Verification boundary:** static source, diff, hash and receipt inspection, plus the three explicitly allowed plan-local commands. No project test, build, dependency installer, generator, packaged executable, validate-task check or timestamp script was run. Suite results below are inspected author evidence, not fresh reviewer suite execution. No prohibited secret file was opened.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | Claude Desktop MSIX setup can skip the backup of an existing config. Step 1 selects the MSIX virtualized file, but the block passes the standard APPDATA file as backupFile. Step 2 therefore checks and backs up a different file, or explicitly skips backup when that standard file is absent. This violates AC-71.4 / PROMPT_STEPS: back up the file being changed before merging. The Claude Desktop golden fixture preserves the same mismatch. | `ui/src/main/mcp-setup-prompt.ts:139`, `:140`, `:170`; `ui/tests/unit/fixtures/mcp-setup-prompt/claude-desktop-user.txt:6` | Make discovery select one actual config destination, then require backup and merge against that same selected file, including MSIX. Add a regression assertion for an existing MSIX config with no standard config; update the affected golden output and rerun affected checks and the full gate. | open |
| F2 | Low | no | behavior | The plan-local static check falsely rejects D-94 and D-97 after execution because its decision lookup reads only the plan/grouping definitions. Those decisions are defined in the work handoffs and walkthrough. The permitted static command exits 1 and would also prevent the existing H2-3 static procedure from passing. No product false-pass or missing decision was demonstrated. | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:587` | Include the two correlated handoff Decision Logs in the definition lookup, or reconcile the decision references with their canonical owners; retain rejection of genuinely undefined decisions. | open |

F1: confidence **High**, subject **deliverable**, finding_kind **behavior**, blocking **true**, ledger `violates: AC-71` (the registered family; precise leaf AC-71.4). F2: confidence **High**, subject **review-scaffolding**, finding_kind **behavior**, blocking **false**. Neither finding is a control-defeat; no mechanism is asserted.

### F1: concrete failure scenario

This is a static branch trace, requiring no access to a user's config:

1. Claude Desktop uses an existing config under the MSIX location named in step 1: `%LOCALAPPDATA%/Packages/Claude_*/LocalCache/Roaming/Claude/claude_desktop_config.json`.
2. The standard `%APPDATA%/Claude/claude_desktop_config.json` does not exist.
3. The generated prompt says to use the MSIX config instead, then says to skip backup if the **standard** file does not exist.
4. The agent follows the prompt and merges into the existing MSIX config with no backup of that file.

The source's `jsonBlock(..., find, backupFile)` arguments and the committed golden text independently show this mismatch. Even when both files exist, the prompt backs up the wrong one. The recorded manual test explicitly used a standard installation, so it does not cover this branch.

## Commands Executed

Every shell process was routed through `rtk proxy`. Exact-evidence commands were redirected under C:/Temp/av-kit and their native status preserved. Bounded source reads used `rtk proxy pwsh -NoProfile -Command 'Get-Content ... -Encoding utf8'`, sometimes with numbered ranges. All relative paths below refer to the worktree.

| Command / observed procedure | Exit | Decisive observation |
|---|---:|---|
| `rtk proxy git status --untracked-files=all` | 0 | Correct branch; implementation is uncommitted, including new source, tests, golden fixtures, plan outputs and handoffs. |
| `rtk proxy git diff HEAD --stat`; `rtk proxy git diff HEAD`; scoped diff reads | 0 | 39 tracked modified paths; untracked paths separately inspected. Complete diff saved as s31b-review-full-diff.txt. |
| `rtk proxy git log -1 --format=%H` | 0 | 6097cf59adc7835fa6062c8bd3d55c679aef4543. |
| `rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py static` | 1 | FAIL: task.md cites D-94, which no decision defines; FAIL: task.md cites D-97, which no decision defines. F2. |
| `rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py selftest` | 0 | PASS PKG_PROBE for equal fixture bytes; expected negative diagnostic for unequal bytes; PASS selftest. The internal FAIL line is an asserted negative case. |
| `rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py scope` | 0 | PASS scope: 77 changed paths since 6097cf59, all listed or closeout; frozen paths unchanged. |
| `rtk proxy git show HEAD:mcp-server/src/index.ts` | 0 | Baseline suffix guard accepts src/index.ts or dist/index.js only; current implementation uses the realpath guard. |
| `rtk proxy git -C P:/zorivest show <commit>:<source-path>`, once for each of the three PROVENANCE rows | 0 each | Source blobs captured only to scratch receipts; comparison results below. |
| PowerShell read-only SHA-256 comparison of gate-result product_file_sha256 and the ten PKG_FILES, using Get-FileHash | 0 | All ten packaged-proof files match. Three of 61 recorded full-gate paths differ: docs/BUILD_PLAN.md, task.md, walkthrough.md. Code/tests/fixtures/config hashes match. |
| PowerShell read-only JSON inspection of full-suite reports and their test file paths | 0 | UI 1006/1006 across 101 files, MCP 446/446 across 31 files, wrong-tree files 0; Electron rootDir is this worktree, expected 159, unexpected/skipped/flaky 0. |
| `rtk proxy rg -n 'require\(\|__require\(\|^import .*from \|^import \{' mcp-server/bundle/index.mjs` | 0 | Runtime external imports are Node builtins; package-looking require strings occur in AJV standalone-code metadata, not executable package loads. |
| PowerShell Get-Content reads of named receipts, Red JSON failures, selected golden output, resource listing and schema/ledger definitions | 0 | Corroborates the evidence and F1; resources/mcp-server holds exactly index.mjs (793592 bytes) and LICENSES.txt (10571 bytes). |

The hash/provenance/tree observations are preserved in `s31b-review-identities.txt`, `s31b-review-provenance.txt`, `s31b-review-gate-tree-audit.txt` and `s31b-review-red-audit2.txt`; decisive values are embedded here. A first numbered-read command failed in shell argument parsing (exit 1), and preliminary Red/tree inspection commands had quoting errors. Their output was not accepted as evidence; corrected read-only commands produced the observations above. No product command ran as a consequence.

## Evidence and Answers to E1–E8

### E1 — TOKEN_BOUNDARY

**Pass for the shipped setup-prompt path.** The builder input contains only client, scope, command, serverPath and appData (`mcp-setup-prompt.ts:24`). Launch entries contain only command, args and the two required environment keys (:53). The new strict IPC schema rejects unknown clients, missing scope and extra token fields (`ipc.ts:109`, `:314`). Its handler (:469) uses the launch dependency and appData and never reads readMcpToken or the MCP credential. Main wires paths and process.execPath only (`index.ts:441`); preload forwards the two selectors; Settings renders/copies text only.

There is no new prompt logging or secret-reading path. Golden fixtures use fixed public paths, and the example contains placeholders plus ELECTRON_RUN_AS_NODE/AVKIT_APP_DATA, without a token or token expansion. IPC tests put a fake credential in deps and assert zero token reads and no credential in the response. Electron tests compare all eleven viewer variants against the token obtained through the old main-process clipboard action.

This is the prompt-channel boundary, not a claim that the entire application has no credential-capable facility: Advanced Copy MCP config deliberately still writes the credential to the system clipboard, and existing clipboard APIs remain. Neither the new channel nor its renderer flow calls that legacy action. No live token was inspected.

### E2 — ENTRY_GUARD

**Pass.** `entry-guard.ts:8-16` compares native realpaths of argv[1] and fileURLToPath(import.meta.url), lowercases on Windows, and returns false on missing argv or any resolution/URL error. It is layout independent for junctions/symlinks, drive-letter case, packaged index.mjs and node dist/index.js. `index.ts:33` has exactly one guarded call to main, so importing createServer in tests does not start a second stdio server.

The unit cases cover own file, junction, Windows drive case, packaged layout, other/missing files and undefined argv. The recorded AC-71.9 Red is a real assertion: the baseline junction launch exits 0 without initialize, rather than failing to import a package. Current process tests and both packaged probes answer initialize.

### E3 — MCP_LAUNCH, SERVER_ENTRY and quoting

**Pass for launch/path contracts.** The dev helper resolves ../../../mcp-server/dist/index.js from ui/out/main; packaged resolves resources/mcp-server/index.mjs. Main uses app.isPackaged, process.resourcesPath and process.execPath. The recorded Electron-node dev spawn and packaged probes cover the resulting launch shape.

JSON.stringify escapes backslashes/quotes in JSON and the constrained TOML basic-string blocks. Spaces stay inside each string/argv value. Claude Code emits a single add line, explicit user/project scope, repeated -e options and a -- separator before quoted executable/server arguments. Its quote/$/backtick refusal is applied to all three path inputs; negative tests cover each position. No local or scopeless add is emitted. These conclusions are about the approved Windows command/config shapes, not fresh CLI execution.

**F1 remains:** correct launch fields do not repair the MSIX backup instruction.

### E4 — bundle, licenses and packaging

**Pass for the reviewed bundle and packaged bytes.** esbuild is exactly 0.28.2; shipped options use bundle=true, ESM, node22, metafile and the createRequire banner, with no external-package list. The built artifact's runtime import sites use Node builtins. AJV's textual require expressions are metadata for standalone-code generation; they are not unresolved runtime package calls. The isolated-copy Node test and packaged isolated-copy probe corroborate independence from repository node_modules for server startup.

License collection follows the last node_modules package segment, including scoped packages, deduplicates package directories, fails if no matching license file exists, sorts the sections, and carries complete text into LICENSES.txt. Current output has these eight sections: @modelcontextprotocol/sdk 1.30.0 (MIT), ajv 8.20.0 (MIT), ajv-formats 3.0.1 (MIT), fast-deep-equal 3.1.3 (MIT), fast-uri 3.1.5 (BSD-3-Clause), json-schema-traverse 1.0.0 (MIT), zod 3.25.76 (MIT), zod-to-json-schema 3.25.2 (ISC). The real-build test derives names from a metafile separately from collectLicenses.

The build uses fixed options, no timestamp and sorted notices; fresh bundle builds in gate92 and the full gate still match the earlier packaged hashes, demonstrating determinism for these pinned inputs. No cross-version/cross-platform reproducibility claim is made. Packaging copies bundle/, dist:prep builds it, and .gitignore excludes it. The actual shipped MCP resource directory contains only index.mjs and LICENSES.txt.

### E5 — test rigor, Red and cleanup

**Meaningful tests, with the MSIX branch gap in F1.** Required launch/IPC/token/guard/UI/bundle behavior has explicit assertions and integration evidence. The prompt/golden tests nevertheless accept a backup target that differs from the chosen MSIX target; there is no regression assertion for that supported branch.

Not every Red is an assertion failure, and the handoffs disclose this correctly: the four MEU-71 new-module files and MEU-92 bundle-licenses file fail to load their not-yet-created modules under the approved S4 exception. The other Reds are relevant assertions: unknown channel, missing UI nodes, missing entry response, old example, old instruction tail and absent packaging pins/bundle. Inspected JSON agrees: MEU-71 UI 17 failed/22 passed, MCP 5 failed/2 passed, Electron 2 failed; MEU-92 5 failed plus its declared load failure. AC-92.4 uses the recorded earlier packaged failure rather than claiming a new assertion Red.

The spawn helpers explicitly distinguish responses from exits/deadlines, and assertions require the response kind and av-kit identity. They do not turn failure into success via catch/return. AC-71.9 kills in finally, closes its backend and removes its junction/temp tree. AC-71.10 kills on settlement and has no child cwd temp directory. Those two helpers do not await exit after kill; they rely on ordinary child termination, so they provide weaker shutdown synchronization than AC-92.1. AC-92.1 now waits for exit/close before deleting its temp cwd, addressing the recorded EPERM without changing assertions. This is a valid setup repair.

D-94 retries the **app button click** and reads the real main clipboard; it never writes the expected result from the test. The prior sentinel triggers the documented Windows clipboard-lock race. The approved retry preserves content/provenance assertions and does not make a permanently broken app copy pass. It proves eventual copy within ten seconds, not guaranteed first-click success during a clipboard lock. No additional product regression from D-94 was demonstrated.

### E6 — receipts, identity and stale/wrong-tree evidence

**Recorded gate and packaged proof agree with the supplied evidence.** The full gate's 17 stage rows, suite JSON and raw tails agree: UI 1006, MCP 446, Electron 159, no failures/skips/flakiness; COUNT_FLOORS is baseline 975/428/157 plus 31/18/2. Suite file names and Playwright rootDir identify this worktree. The gate rebuilds dist and bundle before suites and checks package proof after bundling.

Package result schema is s31b-pkg-probe.v2. The in-place/isolated probes report av-kit 0.1.0, 0.17/0.11 seconds, empty stderr; recorded child exit 1 is the deliberate post-response kill, not an ignored startup failure. All ten identity files independently match. Bundle and packaged entry SHA-256 is `2ee9a90bc366adb8b75dd258e088d1da773c1aad34cb6a36bdedca611cfe5edb`; both license files are `24ee29319a63f6c43dc35d3a1dd879bd2ed40ca459b8d4b972f9331e24c2d7b1`. exe is `34383e87849b8506b6ff4829f4128d60338f7f911cf116e6dca48e3dfe719cfd`. pkg-current rehashes every bound file and refuses changed/missing/unidentified proof; selftest covers these negatives.

HEAD plus working-tree content hashes and lockfile hashes distinguish this uncommitted implementation from the baseline. Independently comparing the 61 gate hashes found only three changed documentation/progress files: rendered BUILD_PLAN statuses, task row evidence/status, walkthrough's subsequent gate/look record. All recorded product source/tests/fixtures/config match. This is evidence reuse for matching product inputs, not a claim of byte identity for every closeout document. The manifest-hash method used at intermediate handoffs is sound when its per-file manifest is retained; HEAD alone would not be enough.

Limits: the full-gate identity is scoped to ui/mcp-server/docs, not a universal environment snapshot; the new inspiration input is outside that hash set and was independently verified here under E7. It records Node/Electron versions but not every inherited environment value. These observations do not establish a concrete wrong-tree/stale product false-pass in this run. F1 instead demonstrates that genuinely passing tests can omit a material prompt branch.

The failed gate71 clipboard run, green92 cleanup run and first packaged launch attempt are retained and accurately disclosed; none is counted as a passing product gate. The packaged tree lacks backend/FFmpeg inputs, as the builder warning and walkthrough say. This probe certifies the MCP entry/startup contract, not a complete installer or authenticated packaged backend workflow.

### E7 — Amendment A-1

**Pass.** Read-only git show of the named Zorivest commits was compared with each local copy, normalizing only CRLF to LF per PROVENANCE:

| Copy | Source commit | LF bytes | Git blob | SHA-256 |
|---|---|---:|---|---|
| globals.css | 61243baff0c141aee318257df2ad844e52e4e83c | 14513 | f12b4614baee11f07eb4512dde34727c1a5e6b81 | cee4f7dea9d4cbe31b31a75e35c426042c963f6668474f90766d971fd154404b |
| gui-actions-index.md | 61243baff0c141aee318257df2ad844e52e4e83c | 18580 | 0425de06becf0a0bebf0a31a210320ab3af209f6 | 15c9f747fe2e3d712e022d3961f5f6f71209c0fbaaf4206b06dafbc7523c8e6d |
| 05n-agent-connect.md | ca693695fba7d25e5faad86daed578d891e5fe22 | 178314 | e864dd8ec88508a69a91520f9215a1ac9ee9ce0d | f2bab595aa4ef6fdf8b4671c22c5f4f9517c263d218da0d6e21914ab9c0e4afa |

All source comparisons were equal, and every blob/hash/size matches PROVENANCE.md. The queue-canon diff changes the source path and two comments only; PORTED_TOKENS and AC-41.3 assertions remain intact. Canon now identifies av-kit as owner and Zorivest as provenance. The resolved issue explicitly overturns the former re-port prescription; no palette product change is concealed.

### E8 — scope and hubs

**Pass.** Independent scope reports all 77 changed paths listed or permitted closeout outputs, with frozen packages/tools/native/openapi.committed.json/11-page-layout unchanged. Git status/diffs agree. Main changes are limited to the four named files. Amendment A-1 paths are explicitly listed.

The four row-10 hubs agree with the code: resources/mcp-server/index.mjs plus LICENSES.txt, prompt IPC/Settings/Advanced layout, no token in client setup, and matrix 7.3/7.5 with correct dependencies. H1 closeout changes are statuses/evidence, not additional behavior. MEU-71/92 are ready_for_review; grouping says in review. H2 remains pending and is not declared complete.

D-95 is a harmless sequencing repair required by green71-main's existing test set. D-96's renderer list duplication is protected by two independent CLIENT_SET pins. D-97 changes executable resolution without weakening the probe. D-98 reuses shipped esbuild options while the license test derives its own package-name oracle. None independently defeats a contract.

## Test Rigor Audit

Grades apply to every new test in the stated groups and the amended cases in existing files; unchanged regression assertions were also inspected in the test diffs.

| File / cases | Grade | Reason |
|---|---|---|
| ui/unit mcp-setup-prompt, all 12 tests | Strong for launch/scope/token/steps; Adequate for backup | Eleven golden variants plus parsed fields and negative inputs. MSIX backup-target subcheck is absent (F1). |
| ui/unit mcp-server-entry (2), mcp-prompt-ipc (4) | Strong | Concrete repo-root/path expectations; strict payload and token-read/effect checks; distinguishes schema error from unknown channel. |
| ui/unit mcp-spawn-electron (3) | Strong | Real Electron-node initialize, first stdout JSON identity, positive/negative fuse fixtures. |
| ui/unit settings-mcp-prompt (8) | Strong | Actual component, ordered nodes, user events, exact clipboard call/status, unsupported/failing channel cases. |
| ui/e2e mcp-setup-prompt (2) | Strong for delivered UI/IPC/copy | Real Electron, real clipboard, all client/scope viewer token exclusions; D-94 limitation above. |
| mcp entry-guard (5), entry-spawn (1) | Strong | Real filesystem/junction and real child RPC; explicit early-exit/deadline failure. |
| mcp example-config (2), appended runtime cases (2) | Strong | Exact launch placeholders, forbidden legacy content, complete ordered prior instructions. |
| mcp bundle (5), bundle-licenses (3) | Strong | Isolated child and packaging pins; exact fixture license sections/error and independent real-metafile coverage. |
| amended gui-actions-audit, clipboard-image-main, ipc-strict-census, login-item-ipc | Strong for changed cases | Channel equality/registration, malformed payloads before effects, actual preload/production testids; TA edits retain prior assertions. |
| amended queue-canon AC-41.3 and settings E2E W4-2/W4-3 | Strong | Token expectations unchanged against verified copy; only disclosure-opening steps added before prior assertions. |
| fixtures, ipc-channels and test-ids support data | n/a | Support inputs, not independent behavioral tests. Claude Desktop fixture currently endorses F1. |

## Checklist Results

Unless a command is named, results below are manual source/diff/receipt observations by **gpt-6.1-sol**, exit **null**.

| Check | Result | Procedure / evidence |
|---|---|---|
| IR-1 live integration/runtime evidence | pass | Inspect real child/Electron tests and matching author receipts; both packaged layouts answer initialize. Backend Settings seam does not replace prompt IPC or clipboard. |
| IR-2 stub behavioral compliance | pass | Inspect Settings seam/fake health backend; required RPC liveness/dependencies behavior and recorded paths are asserted. No new production stub. |
| IR-3 REST error mapping | n/a | No REST write route changed. |
| IR-4 fix generalization | fail | Trace both Claude Desktop destination branches and generated backup step: MSIX does not use the selected file (F1). |
| IR-5 test rigor | fail | Audit all test groups above: no MSIX backup invariant, so current golden/step assertions allow F1 to remain green. |
| IR-6 boundary validation | pass | Strict client/scope IPC schema, malformed/extra-field negatives, builder project-scope rejection; no new REST or MCP input boundary. |
| IR-7 AC coverage/deferral integrity | partial | All 19 leaf ACs appear across the handoffs and have named tests/proof; AC-71.4 is not satisfied for MSIX. No disguised deferral. |
| AV-1 failing-then-passing proof | pass | Inspect Red JSON and Green/full receipts; declared module-load exceptions disclosed rather than called assertion Reds. |
| AV-2 no bypass hacks | pass | Inspect tests/helpers and D-94 retry: assertions remain live; content must come from the app. |
| AV-3 changed paths exercised | partial | UI/IPC/startup/bundle paths asserted, but alternate backup destination omitted (F1). |
| AV-4 no skip/xfail masking | pass | No added skip/only/todo; final Electron unexpected/skipped/flaky all zero. |
| AV-5 no unresolved placeholders | pass | Read product source and source-audit receipt; behavior implemented, no placeholder substituting an AC. |
| AV-6 source-backed criteria | pass | Contract source labels and approved decisions provide the behavior basis. |
| Template IR: source labels / exact validation cells / BUILD_PLAN audit | pass | Read plan/task, procedures, actual hub changes and row evidence. |
| Template IR: post-MEU order | pass | H1 handoffs and review state present; H2 explicitly pending after independent review. |
| Template DR: naming / template / frontmatter | pass | REVIEW-TEMPLATE v2.2, both MEUs, correct absolute target and round 1. |
| Template PR: evidence bundle / FAIL_TO_PASS | pass | Raw author receipts and result JSON agree; identity limitations and post-gate documentation changes disclosed above. |
| Template PR: independent verifier observations | partial | scope/selftest exit 0; static exit 1 due F2, not represented as a pass. |
| Template PR: anti-placeholder / scope | pass | Actual product diff plus independent scope command: 77 paths, no frozen changes. |

```json
{"schema_version":"evidence.v1","check_id":"s31b-review-scope","command":"rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py scope","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"all changed paths versus baseline and Files Modified/closeout allow-list","phase":"targeted","exit_code":0,"result":"pass","tested_state":"6097cf59adc7835fa6062c8bd3d55c679aef4543 plus current uncommitted worktree","output":"PASS scope: 77 changed paths since 6097cf59, all listed or closeout; frozen paths unchanged","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-review-selftest","command":"rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py selftest","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"plan-local read-only verifier negative cases","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current plan_checks.py","output":"Equal-byte fixture PKG_PROBE passes; unequal-byte fixture emits expected FAIL; PASS selftest","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-review-static","command":"rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py static","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"current plan/task/procedure references","phase":"static","exit_code":1,"result":"fail","tested_state":"current plan/task/procedure files","output":"FAIL: task.md cites D-94, which no decision defines\nFAIL: task.md cites D-97, which no decision defines","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-review-msix-backup","procedure":"Trace the claude-desktop branch through jsonBlock and buildSetupPrompt; compare the committed claude-desktop-user golden Find and Back up lines. Consider an existing MSIX config and absent standard APPDATA config, without accessing either file.","observer":"gpt-6.1-sol","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"AC-71.4 backup before merge for the supported MSIX destination","phase":"targeted","exit_code":null,"result":"fail","tested_state":"mcp-setup-prompt.ts and golden fixture matching full-gate recorded hashes","output":"Find selects the MSIX config instead; backupFile remains the standard APPDATA config; generated step 2 explicitly skips backup when that standard file is absent. Existing MSIX config is then merged without its backup.","fresh":true}
```

## Verdict

**changes_required — intent_achieved: partial.** One High blocking product finding (F1) and one Low non-blocking verifier observation (F2). Token isolation, launch paths/entry guard, bundle, notices, packaged startup proof and scope are supported. AC-71.4's backup guarantee is incomplete for a supported Claude Desktop installation.

Mat's L1/L2/L4 observations and Claude Desktop successful manual run support the normal layout and authenticated verification flow. Substituting that run for the plan's Claude Code L3 does not itself warrant a process blocker: Claude Code's emitted launch/scope/step text is covered by its automated contracts, and there is no demonstrated casing regression in that block. It does not prove an actual Claude Code /mcp session, and the manual standard-install run does not address F1. Optional Codex L5 remains unrun.

## Follow-up Actions

1. Route F1 through execution-corrections: bind backup and merge to the selected Claude Desktop destination; add the MSIX-only-config regression and update the affected golden fixture.
2. Rerun affected tests and one fresh full scoped gate after the code/test change, then submit the next round against that tested state. Refresh packaged proof if its bound inputs change.
3. Reconcile F2 during closeout without spending a separate product review round on it.
4. Preserve this report verbatim at the canonical rolling review path and record the matching v2 verdict as round 1. No commit/push is authorized by this report.

Completion-preflight was consulted and the canonical task table read. H1-7 and H2 remain orchestrator work; this dispatched reviewer does not edit their state, execute H2 or claim session DONE. User static-only and JSON-output instructions take precedence over the repository workflow's timestamp-script/chat-suffix instructions.

## Round 2 Recheck — 2026-10-17

**Verdict: approved. Intent achieved: yes. Open findings: 0.** Loop `s31b-exec-2026-10-16-gui-mcp-setup-prompt`, round 2 of 6. F1 and F2 are fixed; no new finding.

### Intent anchor

Session 31b delivers MEU-71 (a per-client MCP setup prompt that the Settings MCP card shows and copies, with no token in any block and a fixed `mcp-server` entry guard) and, under grouping D-56, MEU-92 (a self-contained `esbuild` bundle of the MCP server that the packaged app ships and `MCP_ENTRY_PROBE` proves starts from a built `win-unpacked` tree).

### Scope and independence

Reviewed only the corrections to round 1, their regression assertions and saved execution evidence, with the prior round's accepted surfaces retained unless affected. All commands used `P:/av-kit-wt/s31b-gui-mcp-setup-prompt` as cwd. HEAD remains `6097cf59adc7835fa6062c8bd3d55c679aef4543`; branch/worktree state is the uncommitted implementation described in the dispatch. No plan, product or test file was read from the separate `P:/av-kit` checkout.

Claude Code/Anthropic implemented this work; this Codex/OpenAI reviewer authored none of it. No repository file was written. This receipt report is for the orchestrator to append verbatim to the canonical rolling review and use to replace its frontmatter. No prohibited secret/config file was opened. Reviewed file contents were treated as data.

Applied the execution-review workflow, REVIEW-TEMPLATE v2.2, reviewer role, output-evidence policy and terminal/completion preflight within the user's static-only boundary. The prior round and Session 39 review supplied format calibration. The three permitted plan-local commands were the only project verification code executed. No product tests, builds, generators, packaged executable, validate-task check, timestamp script or additional review dispatch ran.

### Findings and prior finding status

No open or new findings. Historical disposition:

| ID | Prior severity | Status | Evidence |
|---|---|---|---|
| F1 | High, blocking | fixed | `ui/src/main/mcp-setup-prompt.ts:45`, `:135`, `:143`, `:146`, `:177`; regression test `ui/tests/unit/mcp-setup-prompt.test.ts:253`; updated Claude Desktop golden lines 5–7. |
| F2 | Low, non-blocking | fixed | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:52`, `:588`–`:593`; actual D-94 and D-97 definitions in the MEU-71 handoff `:257` and MEU-92 handoff `:159`. |

### R1 — same-file backup, regression test and unchanged outputs

**F1 is fixed in substance.** `clientBlock` now selects the MSIX path when the Claude package folder exists, otherwise the standard APPDATA path, and explicitly requires that one file in every later step. The optional `Block.backup` overrides the fixed-path backup text only for Claude Desktop. Step 2 backs up the file chosen in step 1, appending the required UTC backup suffix, before changing it. Step 3 merges into that selected file and creates it if absent.

| Static case | Selected destination and behavior |
|---|---|
| MSIX folder and config present, standard config absent | Back up and merge the MSIX config. No APPDATA existence test can suppress its backup. |
| Both configs present | Select, back up and merge the MSIX config only. |
| MSIX folder absent, standard config present | Select, back up and merge the standard config. |
| Selected config absent, including an MSIX folder with no config yet | Skip backup of that absent file and create the same selected destination. |

The new test is **adequate for the emitted-prompt contract**. It requires the single-file selection rule and rejects either literal APPDATA or LOCALAPPDATA in the backup line, then requires backup of the chosen file with the prescribed suffix. Missing Find/Back up lines cannot pass. It does not execute a filesystem merge, which is outside this pure text builder's responsibility.

The saved Red is a real assertion failure: 1 failed, 12 passed, with the old Find text shown. Its first failure is the new wording-sensitive Find assertion, so that first diagnostic alone does not isolate the backup defect. Independently, the old step 2's fixed `%APPDATA%` target necessarily fails the new backup assertions at `:262`–`:264`. Thus the complete test catches the original contract violation even though some assertions constrain phrasing. The Green receipt reports 13/13, and the later full gate includes this test. No expectation was weakened to make it pass.

The other valid outputs are unchanged. There are **eleven** supported client/scope combinations (seven user plus four project), hence **ten other goldens**, rather than twelve. All ten retain their round-1 SHA-256 identities. The twelve pre-existing tests also passed in the Red and Green runs. Other clients never set `backup`, so nullish fallback uses the identical original backup template; their builders, client list and project-scope rejection rule are unchanged. The three unsupported project scopes still throw.

### R2 — decision lookup without weakening rejection

**F2 is fixed.** The lookup now concatenates the plan and the two explicitly named work handoffs. It still extracts definitions only through the anchored `^  - id: D-(\d+)$` pattern. D-94 and D-97 have actual matching definition records in their respective handoffs; a prose mention or task citation does not become a definition. The existing carried grouping IDs remain unchanged.

The subsequent set difference and error-return path are unchanged. For example, a task reference to D-999999, absent from those owners and the carried IDs, enters `errs` as `task.md cites D-999999, which no decision defines` and makes `check_static` return 1. This negative conclusion is a source trace, not a claimed mutation-test run. The permitted selftest does not contain a dedicated undefined-decision case. Actual static execution now exits 0; saved pre-fix Red reports precisely the two original undefined IDs. No catch, unconditional pass, broad citation-as-definition scan or expanded arbitrary-ID allowance was added.

### R3 — regressions, token boundary, scope and current gate

**No correction-induced regression or new scope path found.** Comparing the preserved H1-2 gate's embedded manifest with the replacement gate shows only three changed product source/test/fixture inputs: the prompt builder, its unit test and the Claude Desktop golden. Other differences are plan/tooling/progress/review records. The prompt change adds prose selection/backup text only: no I/O, token parameter, credential read, logging, IPC payload, client or scope is added. The launch fields, token exclusions, entry guard, bundle inputs and packaged launch path retain the round-1 accepted state.

**The replacement gate is valid evidence for the current product inputs.** It ran 2026-10-17 14:36:07–14:41:00 (-04:00), after the 14:35 Red/Green correction, on Node v24.19.0 / Electron 42.9.3. All 17 recorded stages exit 0. Saved raw checks and suite JSON agree: UI 1007/1007, MCP 446/446, Electron expected 159 with unexpected/skipped/flaky all 0; COUNT_FLOORS is +32/+18/+2 over 975/428/157. Vitest test-file paths have zero wrong-tree entries; Playwright rootDir is this worktree's `ui/tests/e2e`.

Independent read-only hashing compared all 63 recorded paths with current bytes. Only these differ:

- `implementation-plan.md`: reversing exactly the two documented D-79/D-89 wording edits in memory reproduces the gate's hash. No contract meaning changed.
- `walkthrough.md`: subsequent review/correction/budget reporting, including the replacement gate summary.
- `gate-result.json`: the gate snapshots the existing result before overwriting it with this run's result; its own earlier hash cannot identify the newly written result.

All recorded product source, tests, fixtures, configuration, task and verifier bytes match, as do both lockfiles. All ten packaged-proof bound files independently match their recorded hashes, both probes remain recorded as `started`, and bundle/packaged entry SHA-256 remains `2ee9a90bc366adb8b75dd258e088d1da773c1aad34cb6a36bdedca611cfe5edb`. Consequently the prompt correction does not require new MCP packaging proof. This certifies the scoped MCP startup claim, retaining round 1's limits concerning missing backend/FFmpeg packaging inputs and environment coverage.

The standalone `s31b-gate-result-h1-2.json` named in the correction notes was absent. The preserved `s31b-run-gate-h1-2.txt` contains the complete original result JSON, which supplied the comparison above. Current-gate identity and results do not depend on that missing duplicate. No finding is raised for it.

### Commands executed and observed results

Every shell process used `rtk proxy`, with this worktree as cwd. Exact-evidence output was redirected beneath `C:/Temp/av-kit`, the native exit captured immediately, and the completed receipt read back. Bounded reads used `powershell -NoProfile -Command Get-Content ...` with UTF-8/ranges where appropriate; `pwsh` supplied SHA-256/JSON inspection.

| Command or read-only procedure | Exit | Decisive result |
|---|---:|---|
| `rtk proxy git status --short`; `rtk proxy git diff --stat`; scoped `git diff -- <plan> <plan_checks.py>` | 0 each | Uncommitted worktree; inspected tracked changes and correction-owner definitions. New prompt/test/fixture files were read directly. |
| `rtk proxy git log -1 --format=%H` | 0 | `6097cf59adc7835fa6062c8bd3d55c679aef4543`. |
| `rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py static` | 0 | `PASS static: 21 rows, 20 -Check names, 19 ACs covered`. |
| `rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py selftest` | 0 | `PASS PKG_PROBE` for equal fixture bytes; expected `FAIL: PKG_PROBE ... byte_equal False ...` negative diagnostic; `PASS selftest`. |
| `rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py scope` | 0 | `PASS scope: 79 changed paths since 6097cf59, all listed or closeout; frozen paths unchanged`. |
| `rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s31b-r2-audit.ps1` | 0, final run | Read-only JSON/SHA-256 audit described above: 63 paths, three explained non-product differences; ten other goldens unchanged; both locks and ten packaged-proof files match; correct-tree suite results. |
| `Get-Content`, `Get-ChildItem`, and targeted `rg -n` reads | 0 for decisive reads | Inspected workflow/role/template/prior verdict, plan/task/correction walkthrough, both handoff decision logs, prompt and full unit test, fixture listing, gate procedure, Red/Green/static/selftest receipts, raw gate and suite-check receipts, schema. |

Scratch diagnostics not accepted as proof: the first hash audit exited 1 because the standalone old JSON was missing; the corrected audit read the embedded JSON and passed. One narrow old-source search returned 1 (no matches); a later receipts search returned 2 for inaccessible unrelated temporary subdirectories and was not used to claim absence. The memory-registry search provided no relevant evidence. No forbidden test/build command followed these diagnostics.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-4 correction generalization | pass | All Claude Desktop destination/existence branches above use one selected file; other clients retain their prior output. |
| IR-5 changed-test rigor | pass | Test rejects the old fixed backup path; Red/Green 12+1 failure to 13 passes; wording sensitivity and lack of filesystem execution disclosed above. |
| Token and scope boundary | pass | Only text-building product source changed; accepted IPC/renderer/guard/bundle inputs unchanged; scope exits 0. |
| Decision-definition rejection | pass | Restricted owner expansion and unchanged undefined-ID failure branch; actual static exit 0. |
| Fresh full-gate applicability | pass | Saved suite output agrees with current product hashes and correct worktree; ten packaged identities match. Product suites were not rerun by the reviewer. |

```json
{"schema_version":"evidence.v1","check_id":"s31b-r2-static","command":"rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py static","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"current plan/task/procedure decision references","phase":"static","exit_code":0,"result":"pass","tested_state":"6097cf59adc7835fa6062c8bd3d55c679aef4543 plus current uncommitted worktree","output":"PASS static: 21 rows, 20 -Check names, 19 ACs covered","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-r2-selftest","command":"rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py selftest","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"plan-local verifier selftests","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current plan_checks.py","output":"PASS PKG_PROBE for equal fixture bytes; expected FAIL for byte_equal False; PASS selftest","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-r2-scope","command":"rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py scope","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"changed paths versus approved scope and baseline","phase":"targeted","exit_code":0,"result":"pass","tested_state":"6097cf59adc7835fa6062c8bd3d55c679aef4543 plus current uncommitted worktree","output":"PASS scope: 79 changed paths since 6097cf59, all listed or closeout; frozen paths unchanged","fresh":true}
```

### Verdict and handoff

**approved — intent_achieved: yes.** F1 and F2 are fixed. No open findings, no further correction requested. Static review supports the supplied replacement gate for the current product tree; it is inspected author execution evidence, not fresh reviewer runtime execution.

Completion-preflight was consulted and the canonical task table read. H1-7 and H2 remain orchestrator-owned follow-through; this review does not mark them complete or claim session DONE. The orchestrator must preserve this round's report/verdict and continue its authorized closeout. No commit or push is authorized by this review. User-specified receipt-only writes and JSON final output take precedence over repository timestamp/chat-suffix instructions.
