---
date: "2026-10-16"
review_mode: plan
target_plan: P:/av-kit/docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md
verdict: approved
findings_count: 0
round: 3
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-16-gui-mcp-setup-prompt

> **Review Mode**: plan
> **Verdict**: changes_required
> **Reviewer**: gpt-6.1-sol, independent OpenAI reviewer of Claude Code's Anthropic-authored plan.
> **Ledger round**: 1; loop `s31b-plan-2026-10-16-gui-mcp-setup-prompt`.

## Intent Anchor

> Session 31b delivers MEU-71 (a per-client MCP setup prompt that the Settings MCP card shows and copies, with no token in any block and a fixed `mcp-server` entry guard) and, under grouping D-56, MEU-92 (a self-contained `esbuild` bundle of the MCP server that the packaged app ships and `MCP_ENTRY_PROBE` proves starts from a built `win-unpacked` tree).

Intent achieved: **partial**. The proposed product design addresses the setup and packaging defects, but the final gate can certify packaged startup from stale evidence while the required packaged entry is missing.

## Scope

Reviewed the main checkout **P:/av-kit**, branch **main**, HEAD **4a97483669332de67abd434ccd6c2f073cfd6316**. No execution worktree exists yet.

Primary targets: `implementation-plan.md`, `task.md`, `validate-task.ps1` and `plan_checks.py` under `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/`. Plan-local basenames below refer to that directory.

Reviewed the complete specified triage/plan-time diff: grouping, known-issues YAML, MEU SSOT and rendered registry, distribution spec; `docs/BUILD_PLAN.md` has no current diff. Sampled distribution/MCP/GUI canon, grouping D-1–D-7/D-55/D-56, both issue records, Session 38's peer plan verifiers and rolling report, and Session 32's recorded packaged failure/probe implementation. Traced current main IPC/preload/wiring, Settings card, server entry/config/client, package/build configuration, regression tests and reporter wrappers.

All 20 task rows are unchecked. Both MEU implementation handoffs are absent and scheduled. Existing scripts, regression files and invoked tooling paths inspected exist; proposed feature modules/tests/fixtures and MEU-92 registration are explicitly scheduled. The untracked `.claude/settings.local.json` was observed by git status and was not opened.

Only the assigned report and scratch receipts under C:/Temp/av-kit were written. No repository file, live client configuration or token file was opened or changed. No product tests, builds, installers, generators, package managers or validate-task checks were run.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | control-defeat | AC-92.4 can pass using stale packaged evidence after the packaged entry is missing or its inputs change. pkg_result_passed checks only the saved passed boolean; gate92 does the same, and the full gate rebuilds the source bundle without rebuilding or revalidating win-unpacked. After a successful row-8 probe, removing ui/dist/win-unpacked/resources/mcp-server/index.mjs leaves these completion checks satisfied although the required packaged entry no longer exists. Confidence: High. Subject: committable-tooling. mechanism: task-row-completion-predicate. Violates AC-92 (specifically AC-92.4), PR-4/PR-8 and the plan's validation input-binding contract. | docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:337; docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:267; docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:313 | Bind packaged evidence to the current packaging inputs and produced executable/entry/licence hashes, reject missing or changed artifacts, and rerun pkg-probe when that identity changes. Add negative verifier cases for a removed packaged entry and a changed bundle/configuration after a passing probe. | open |

### Decisive static trace for F1

1. Row 8 creates the fresh packaged proof, but `pkg_result` (plan_checks.py:442–458) stores hashes and a commit without a later current-state comparison.
2. `pkg_result_passed` (plan_checks.py:337–338) returns only file-exists and saved `passed is True`. `floors` uses this as the entire runtime-AC oracle (:359–363). `gate92` likewise reads only `$r.passed` (validate-task.ps1:267–268).
3. The full gate rebuilds `mcp-server/bundle` and the development UI, then calls `floors`; it never builds, inspects or launches `win-unpacked` (validate-task.ps1:305–355).
4. Concrete counterexample: after a passing packaged probe, remove `ui/dist/win-unpacked/resources/mcp-server/index.mjs`, leaving the saved report untouched. The local bundle/unit/dev-Electron suites have their own inputs, so none of the listed checks detects this removal. Runtime AC-92.4 remains accepted while its required deliverable is absent. A source-state variant is a packaging filter that excludes index.mjs after row 8: the declared from/to/script pins can remain intact, but the full gate never builds that changed configuration and still accepts the old packaged result.

This is a demonstrated false-pass by source tracing, not a request to deepen predicate formatting. No mutation or executable counterexample was run. Reuse of unchanged, bound packaged evidence is acceptable; it must fail closed when its actual inputs or artifacts change.

## Checklist Results

Manual observations below were made by **gpt-6.1-sol**, through the cited file/line reads, diffs and existence inventories. They have null exit codes; successful read commands are not product passes.

### Plan Review (PR)

| Check | Result | Observed evidence |
|-------|--------|-------------------|
| PR-1 Plan/task alignment | pass | Same two proposed MEUs, test-first order, explicit handoffs, and row-0 decline stop path. |
| PR-2 Not-started confirmation | pass | All 20 rows unchecked; product changes absent from initial git status; implementation handoffs/worktree absent. |
| PR-3 Task contract completeness | pass | Owner, deliverable, exact validation, dependencies, context strategy and status supplied; static sees 20 rows. |
| PR-4 Validation realism | fail | Invoked executables/scripts exist or are scheduled; packaged runtime completion has F1. |
| PR-5 Source-backed planning | pass | FIC/decisions identify spec, local canon, research or pending human ruling; D-56 is not presented as approved. |
| PR-6 Handoff/corrections readiness | pass | Separate MEU-71/92 handoffs and rolling reviews named. Round-2 census gate is inapplicable. |
| PR-7 Scope discipline | pass | Out-of-scope rows have substantive bases; guard is in scope and dependencies have a proposed owner. Scope inventories the whole repository rather than selected subtrees. |
| PR-8 Reachability and negative oracles | fail | Prompt and server production call chains are explicit; F1 breaks the packaged-runtime oracle. |
| PR-9 Single-statement discipline | pass | Named contracts govern shared rules. Swept repeated names/counts; no materially conflicting live value found. |

### Docs Review (DR)

| Check | Result | Observed evidence |
|-------|--------|-------------------|
| DR-1 Claim-to-state match | pass | MEU-71 execution_plan and Session 31b plan folder set; D-77/D-78 distribution Docs row present. No implementation completion claimed. |
| DR-2 Residual old terms | pass | Current suffix guard, dist packaging and old token-bearing example are explicitly inventoried for correction. |
| DR-3 Downstream references | pass | SSOT/rendered registry align; 05/06/07/matrix reconciliation is scheduled. No current BUILD_PLAN diff to misrepresent as a change. |
| DR-4 Verification robustness | fail | Missing packaged entry can remain certified (F1). Other proposed positive/negative tests address the intended surfaces. |
| DR-5 Evidence auditability | pass | Exact verifier commands/exits/output embedded below; source-level counterexample is reproducible by inspection. |
| DR-6 Cross-reference integrity | pass | Pending MEU-92 registration includes dependencies, anchor and matrix slot; Docs-placement changes have local justification. |
| DR-7 Evidence freshness | partial | static/selftest freshly observed; packaged proof is future work and its reuse has F1. |
| DR-8 Completion versus residual risk | pass | Draft/unstarted status preserved; no runtime success claimed by this review. |

### Information Retrieval and adversarial checks

All 19 FIC ACs have source cells and are assigned to tests or the explicit runtime probe. Post-MEU handoff, registry, review, reflection and metrics rows exist. Error cases cover invalid client/scope/payload, missing launch dependency, missing token, path quoting, unavailable API, missing licence and absent bundle. No planned skip/only/todo or assertion weakening was found. The five MEU-specific load-tolerated files are separately considered in Q7.

```json
{"schema_version":"evidence.v1","check_id":"s31b-plan-static","command":"rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py static","cwd":"P:/av-kit","scope":"plan/task/script structure","phase":"planning","exit_code":0,"result":"pass","tested_state":"main 4a97483669332de67abd434ccd6c2f073cfd6316 plus inspected uncommitted Round-1 plan/triage files","output":"PASS static: 20 rows, 19 -Check names, 19 ACs covered","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-plan-selftest","command":"rtk proxy python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py selftest","cwd":"P:/av-kit","scope":"stdlib-only plan-local selftest","phase":"planning","exit_code":0,"result":"pass","tested_state":"same inspected Round-1 files","output":"PASS selftest","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-packaged-proof-static-trace","procedure":"Trace row 8 through pkg_result, gate92 and the full gate's floors call; evaluate removal of the packaged index.mjs after a passing probe without changing the saved JSON.","observer":"gpt-6.1-sol","cwd":"P:/av-kit","scope":"AC-92.4 packaged-runtime completion","phase":"planning","exit_code":null,"result":"fail","tested_state":"Round-1 plan_checks.py and validate-task.ps1 read directly","output":"pkg_result_passed and gate92 inspect only passed=true; the full gate never reads or rebuilds win-unpacked. Missing packaged entry is not rejected (F1).","fresh":true}
```

The selftest exercises helper behavior, including unhandled-error detection and scope negatives. Its PASS does not execute Vitest/Playwright report pipelines, Windows spawn behavior or packaging.

## Commands Executed

Each process used unfiltered `rtk proxy`, all-stream receipts under C:/Temp/av-kit, immediate saved child exit, then completed-receipt reads.

- `rtk proxy git status --short` — exit 0: five modified triage/canon files, untracked plan folder and local Claude settings. Git's config-access warnings were retained.
- `rtk proxy git log -1 --format=%H%n%D` — exit 0: HEAD `4a97483669332de67abd434ccd6c2f073cfd6316`, main.
- `rtk proxy git diff -- .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md .agent/context/known-issues.yaml .agent/context/meu-registry.md .agent/context/meu-status.yaml docs/BUILD_PLAN.md docs/build-plan/07-distribution.md` — exit 0. Reviewed the full diff; line-ending warnings retained.
- The two permitted plan-local verifier commands above — both exit 0, output embedded.
- `rtk proxy rg -n -e 'COUNT_FLOORS|NEW_MODULE_FILES|MCP_ENTRY_PROBE|ENTRY_GUARD|TOKEN_BOUNDARY|TEST_AMENDMENTS' docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/task.md docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py` — exit 0; complete named-contract sweep retained.
- `rtk proxy rg -n 'SERVER_INSTRUCTIONS|instructions|tools/list|listTools|snapshot|baseline' mcp-server/scripts/audit/run.ts mcp-server/scripts/audit` — exit 0; audit discovery/baseline concern tool surfaces and actions, not SERVER_INSTRUCTIONS.
- Read-only `rtk proxy python -X utf8 -c ...` file/line excerpts and Path.exists inventories loaded the required protocol/context/template, targets, named canon, peer scripts/report, source/tests, reporter configuration, review schema and contract vocabulary. Relevant existing tool/regression paths exist; the future worktree/handoffs do not. No node_modules directory currently exists at the four C:/Temp hermetic ancestors inspected.
- `rtk proxy powershell -NoProfile -Command "Get-Content -LiteralPath '.agent/workflows/plan-critical-review.md'"` loaded the protocol first, exit 0. A subsequent Python context read initially failed with cp1252 UnicodeEncodeError, exit 1; the UTF-8 retry succeeded, exit 0. This was a read failure, not product evidence.
- A lightweight memory registry search found no relevant Session 31b/MEU-71/92 setup-prompt record. No memory-derived project fact was used.
- Final report readback confirmed the required frontmatter, one finding and saved report; final `rtk proxy git status --short` exited 0 and matched the initial repository status.

## Answers to Q1–Q10

### Q1 — TEST_AMENDMENTS

**I explicitly approve TA-1, TA-2 and TA-3 as written**, independently of the overall refusal.

TA-1 adds exactly the new strict-payload channel to the test-side list and census, and raises the three existing count-pin sites from 20 to 21. It correctly stays out of IPC_NO_PAYLOAD. TA-2 extends the audit resolver and control inventory for the new indexed action; it preserves the existing registration/preload checks. TA-3 opens the now-closed Advanced disclosure before the unchanged visibility/action assertions. These are minimal consequences of distribution UI/IPC canon and satisfy AGENTS' source-backed independent-review amendment requirement. No other expectation change is approved.

### Q2 — D-56 / MEU-92

**The bundle is the appropriate proposed fix.** The package has ESM SDK/Zod dependencies, while extraResources currently ships only tsc output. Bundling those dependencies into index.mjs avoids shipping a second production node_modules installation. The createRequire banner addresses bundled CommonJS use of Node require; the metafile-driven licence inventory covers included transitive packages. The exact esbuild pin and lockfile change are appropriately scoped. Successful hermetic startup remains necessary; interop failure cannot be waived.

MEU-92 owns scripts, notices, packaging inputs and a real packaged-executable probe, with no invented tool/API work. If Mat declines D-56, **row 0's stop path is sound**: correct the plan and scripts, retain index.js, remove MEU-92's tasks/ACs, then re-review before execution. The unchanged two-MEU plan cannot simply continue. That reduced plan would deliver MEU-71 with an explicit unresolved packaged-dependency limitation; it would not achieve this loop's full registered Goal.

### Q3 — ENTRY_GUARD and real Red

**The realpath comparison is sound for these launch forms.** The junction argument and import.meta.url resolve to the same built file; plain dist/index.js and bundled index.mjs likewise compare to themselves. An imported server does not match the test runner's entry. Undefined/missing paths fail closed.

The current suffix guard checks argv[1], not the resolved file identity. The proposed argument ends in /resources/mcp-server/index.js, so it matches neither accepted suffix (mcp-server/src/index.ts:31–34). AC-71.9 therefore has a real behavior Red on initialize. AC-71.8 separately has the explicitly tolerated missing-new-module Red; it should not be described as an independently observed old-function assertion failure. No process was launched in this review.

### Q4 — MCP_LAUNCH / FUSE_PIN

**The launch shape is sound:** the app executable is absolute, the script is one absolute argument, and ELECTRON_RUN_AS_NODE selects Node execution without shell quoting inside JSON/TOML argument arrays. The dev resolver reaches the repository's mcp-server/dist; packaged resolves resources/mcp-server/index.mjs.

AC-71.10 exercises the dev executable and first stdout line, while AC-92.4 exercises av-kit.exe itself. The static FUSE_PIN is a configuration regression pin; it is not a substitute for the packaged launch. The implementation must obtain the actual binary from ui/node_modules/electron: ui/vitest.config.ts aliases the bare electron import to an Electron stub. The plan's explicit real-binary requirement allows doing this without changing that config. Packaged proof freshness needs F1's correction.

### Q5 — TOKEN_BOUNDARY

**The new prompt path has no structural need for the API token.** The builder takes paths, the handler receives launch metadata and appData, and the readMcpToken spy must remain unused. New IPC request/reply and prompt clipboard text contain no token; no logging is specified. Server config resolves AVKIT_APP_DATA and then reads its own descriptor/token (config.ts:30–42, 156–177), so the same absolute path works across the seven same-user clients without client-specific secret interpolation.

The preserved Advanced copy/pin action intentionally writes the MCP token to the clipboard inside main; its IPC reply remains only an acknowledgement (ipc.ts:410–422). That existing behavior is outside the new prompt boundary. Synthetic token strings are necessary negative-test fixtures, not live credentials; Electron's T must come from its isolated test app data. No real token/config file should be a fixture or receipt input.

### Q6 — Verifier soundness

**Mostly sound, with the material exception F1.** vitest-red merges both projects, rejects unrelated load failures/unhandled errors/skips, and requires Red coverage for each non-Electron/non-runtime AC. The boundary-aware AC pattern prevents AC-71.1 matching AC-71.12. floors requires a passing AC title, baseline-plus-new counts, zero failures/flakiness and no increased Playwright skips. A genuinely absent required AC title does not slip through.

e2e-red requires an unexpected result containing an expect failure for each Electron AC and rejects top-level collection errors. It does not classify every other spec error as strictly as vitest-red; Green/full-gate checks still reject those failures. These checks verify reported AC coverage, not the semantic quality of an assertion carrying an AC label.

mcp-probe now returns failure for missing files/no response/wrong first line, unlike Session 32's record-only probe. pkg-result checks fresh byte equality, nonempty notices and both probe records at creation. Neither its saved commit/hashes nor the packaged artifact's continued existence is checked by consumers: **AC-92.4 can false-pass there**.

scope inventories whole-repository committed, dirty and untracked changes against baseline.sha, then applies frozen/main-file restrictions and the explicit allowlist. No concrete bypass for an unlisted tracked product/root-config change was found. As usual, git-ignored build outputs are outside that source-diff inventory; it is not a packaged-output integrity check.

### Q7 — Assertion Red / NEW_MODULE_FILES

**The import partition is correct.** mcp-prompt-ipc can import existing IPC/preload modules; entry-spawn uses builtins and the already-built server; Settings uses the existing card with API mocks; bundle.test uses builtins and asserts file existence before copying/spawning. These can fail on the intended assertion rather than a missing implementation import.

The four MEU-71 tolerated files are mcp-setup-prompt, mcp-server-entry, mcp-spawn-electron and entry-guard; each imports a new module/export. MEU-92 additionally tolerates bundle-licenses. No extra tolerance is needed for the existing-module files. Actual failures remain execution evidence: especially ensure unknown-channel IPC is asserted on the returned result rather than followed by an unsafe value dereference.

### Q8 — CLAUDE_CODE_BLOCK parsing

**The argument order agrees with the recorded CLI help.** The help declares `[options] <name> <commandOrUrl> [args...]`, gives `claude mcp add my-server -e API_KEY=xxx -- npx my-mcp-server` as its own example, and declares -e variadic (receipt lines 1, 13–17, 25, 29–30). Repeated -e pairs followed by -- protect the executable from env-value consumption. Explicit --scope removes the dangerous local default. This is static help confirmation, not execution of registration commands.

### Q9 — Windows spawn determinism / cleanup

**The test design is feasible, but cleanup and timing cannot yet be certified because the test files do not exist.** The directory junction avoids ordinary file-symlink privilege requirements; isolated temp app data plus a fake backend can prove liveness versus token_missing. The current old guard supplies the intended early exit.

Implement the declared assertion-on-exit/deadline contract with an explicit deadline shorter than the test runner timeout, close/error event handling, and finally/afterEach teardown that kills and awaits the child before removing its junction/temp directory and closing the backend. Remove inherited AVKIT_API_TOKEN/API_BASE overrides for the no-token case. AC-92.1 should assert missing bundle before spawning. These are concrete ways to satisfy the existing task contract, not claims of observed tests.

The Python packaged probe has a bounded polling loop and explicit kill/communicate on its normal path. Its subprocess lifecycle was inspected only; unexpected spawn/pipe errors currently fail the command rather than produce passing evidence. No live Windows cleanup was tested.

### Q10 — Goldens / quoting / audit skip

**Eleven goldens is correct:** seven user blocks plus four supported project blocks. JSON.stringify supplies JSON quoting and valid escaped TOML basic strings for the Windows paths described. Double-quoted Claude Code arguments preserve spaces/backslashes in the relevant shells, while PATH_QUOTE_ERROR rejects quote, dollar and backtick characters that would break that shell form. The actual fixtures are future deliverables, so their bytes and independent expected values remain for execution review; do not generate expected goldens from the builder under test.

**Skipping mcp-audit is justified by unchanged tool/schema/annotation surfaces**, with full MCP tests, the added instructions assertion and the transport probes retained. The audited discovery path collects tools/list and action baselines, not server instructions. The plan's claim that running an audit necessarily rewrites the baseline is too broad: run.ts:583 requires updateBaseline and a baseline path. That wording does not affect the scope-based skip and is not a delivery blocker.

## Verdict

**changes_required** — one High blocking finding, F1. The setup/token/entry-guard design and proposed bundle strategy are otherwise coherent. This review explicitly approves TA-1–TA-3; it does not authorize execution or decide grouping D-56.

Residual uncertainty: no golden fixture, spawn test, Electron launch, bundle interop, licence enumeration or packaged build was executed here. The read-only static/selftest passes establish only their stated verifier checks.

## Follow-up Actions

1. Resolve F1 through /plan-corrections: bind packaged completion evidence to current inputs/artifacts and add the two specified negative cases. Preserve this loop's Round-1 history.
2. Resubmit the corrected plan for independent review with the required correction census.
3. After independent approval, Mat rules on D-56 and authorizes execution. If declined, take the documented plan-correction/re-review stop path.
4. Dispatcher copies this report verbatim from **C:/Temp/av-kit/dispatch/s31b-plan-review-report.md** to **.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md**.

Review-only closeout: canonical task/readiness state inspected; all implementation rows intentionally remain unstarted. Report destination follows the user's receipts-only override. No correction workflow or execution was started.

---

## Corrections Applied — 2026-10-16 (author: Claude Code, Opus 5.5; /plan-corrections after round 1)

Verdict is set to `corrections_applied`. Approval belongs to the independent reviewer in round 2.

| Finding | Correction | Where |
|---|---|---|
| F1 (High, control-defeat): AC-92.4 passes on stale packaged evidence | **`PKG_EVIDENCE`.** `pkg-probe-result.json` is now schema `s31b-pkg-probe.v2`, and its `identity` block holds the SHA-256 of all ten `PKG_FILES`: `av-kit.exe`, the packaged `index.mjs` and `LICENSES.txt`, the source bundle `index.mjs` and `LICENSES.txt`, `ui/electron-builder.yml`, and both `package.json` / `package-lock.json` pairs. `byte_equal` covers both bundle files. `pkg_evidence_errors()` replaces `pkg_result_passed()`. It refuses the proof if the result file is missing, if `passed` is not true, if `identity` is absent (the v1 shape), or if any bound file is missing or changed. It backs `floors` and the new `pkg-current` command. Row 9 (`gate92`) calls `pkg-current` in place of reading `$r.passed`. The full gate adds stage `gate-pkg-current` right after `gate-mcp-bundle`. `pkg-result` now takes 2 arguments (in-place.json, hermetic.json) and derives the files from `PKG_FILES`. | `plan_checks.py` (PKG_FILES, pkg_identity, identity_errors, pkg_result, pkg_evidence_errors, pkg_current, floors, dispatch table); `validate-task.ps1` (pkg-probe, gate92, gate stage list); `implementation-plan.md` (new `PKG_EVIDENCE` contract row, `COUNT_FLOORS`, §5 stage list, §Validation, D-84 chosen/reasoning); `task.md` rows 9 and H1-2 |
| F1 negative tests | `_selftest_pkg_evidence()` runs from `selftest` and uses temp files only. It checks: a fresh proof passes; a removed packaged entry → `missing`; a changed bundle → `changed`; a changed `electron-builder.yml` → `changed`; a v1-shape proof with no identity → refused for all 10 files; a packaged entry that differs from the bundle → `pkg_result` returns 1. | `plan_checks.py` |
| Non-blocking (Q10 note) | The `mcp-audit` skip rationale no longer says the audit "rewrites the committed baseline" (the update is opt-in, `run.ts:583`). It now says the audit covers tool surfaces, not the server instructions. | `validate-task.ps1` gate skip string; `implementation-plan.md` §5 |

TA-1..TA-3 and the D-56 / MEU-92 design were approved in round 1 and are unchanged.

**Commands executed**
- `uv run python docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py selftest` → `PASS selftest`. The `FAIL: PKG_PROBE: … byte_equal False` line just before it is the expected negative case.
- `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check static` → exit 0 (`PASS static: 20 rows, 19 -Check names, 19 ACs covered`; `PASS selftest`; `PASS task-lint`). Receipt: `C:/Temp/av-kit/s31b-run-static.txt`.
- All five plan files are still CRLF (`file`).

**Census** (receipt `C:/Temp/av-kit/census-s31b-r1-f1.txt`; `rg -F` over the plan folder and this review). Variants swept: `pkg_result_passed`, "a passing `pkg-probe-result.json`", "rewrites the committed baseline", "packaged probe passed", `s31b-pkg-probe.v1`, `$r.passed`, the four-argument `pkg-result` call, `PKG_EVIDENCE`, `pkg-current`. The plan folder has 0 old-value hits. The 4 remaining hits are in this review's round-1 evidence (lines 42, 47, 97), which quotes the pre-correction code and stays verbatim.

Blast-radius census: 5 values changed, 9 variants swept, 11 sites found, 11 updated, 0 confirmed consistent.

---

## Round 2 Recheck — 2026-10-16

**Verdict: changes_required — PR-6 pre-verdict procedural gate.** The corrected implementation has **not** been substantively rechecked this round. The correction census is truncated and lacks per-hit dispositions. This is the procedural exception in `.agent/workflows/plan-critical-review.md:258,289–293`, not a newly severity-rated product finding.

### Intent Anchor

> Session 31b delivers MEU-71 (a per-client MCP setup prompt that the Settings MCP card shows and copies, with no token in any block and a fixed `mcp-server` entry guard) and, under grouping D-56, MEU-92 (a self-contained `esbuild` bundle of the MCP server that the packaged app ships and `MCP_ENTRY_PROBE` proves starts from a built `win-unpacked` tree).

Intent achieved: **partial** for review approval purposes; the correction's ability to achieve the whole goal remains unverified. This does not assert that the corrected scripts still contain the round-1 defect.

### Scope and review boundary

Independent reviewer: **gpt-6.1-sol**, OpenAI/Codex; author: Claude Code, Anthropic. Loop: `s31b-plan-2026-10-16-gui-mcp-setup-prompt`, ledger round **2**. Checkout: `P:/av-kit`, main, HEAD `4a97483669332de67abd434ccd6c2f073cfd6316`.

Read the protocol, operating contract, template 2.2, canonical round-1 report and correction section, and the named census receipt. Read task.md for draft/unstarted status and the review boundary. All 20 task rows remain unchecked. Git status shows the five modified triage/canon paths, the untracked plan folder, canonical review and `.claude/settings.local.json`; the latter was not opened.

R1 (bound-file completeness and stale-proof rejection), R2 (fresh-install/rebundle compatibility), and R3 (remaining substantive defects) are **not_run** after the PR-6 gate. No corrected-code conclusion is inferred from the author's selftest claim. No product tests, builds, package managers, generators, validate-task checks, secret files or external websites were accessed. No repository file was written.

### F1 recheck table

| Finding | Round-1 status | Round-2 status | Evidence |
|---|---|---|---|
| F1 — AC-92.4 accepts stale packaged evidence | open; High, blocking, committable-tooling/control-defeat; mechanism: task-row-completion-predicate | **still_open** — correction unverified, not demonstrated still defective | PR-6 stops substantive review: `C:/Temp/av-kit/census-s31b-r1-f1.txt:1–32`; canonical correction log `:204–219`. No fixed/regressed determination was made. |

### Findings and procedural gate

**No new severity-rated finding.** F1 retains its historical High severity and open status pending a permissible recheck. The cumulative findings count remains **1**. The structured verdict carries that existing finding, rather than inventing a severity for PR-6, because the requested v2 JSON schema requires a blocking finding for `changes_required`. Its status does not constitute a second demonstration of the stale-proof mechanism.

| ID | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High (carried from round 1) | yes | control-defeat | Round-1 AC-92.4 stale-packaged-evidence finding remains unverified because PR-6 prevents this recheck. The census receipt is truncated and the correction log lacks per-hit dispositions. No new claim that the corrected code false-passes. Confidence: High in this review status. Subject: committable-tooling. mechanism: task-row-completion-predicate. Original violated contract: AC-92, specifically AC-92.4. | .agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:42; C:/Temp/av-kit/census-s31b-r1-f1.txt:1; .agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:217 | Supply the complete unfiltered census and a file:line disposition for every hit, then recheck F1 and the correction's build/gate compatibility. Preserve the existing ledger and report history. | open |

Decisive observations:

- Receipt lines 1 and 6 provide only `pkg_result_passed => 3` and `$r.passed => 1`; they do not inventory those four hits. The historical-exemption claim in the log cannot replace the raw hit inventory.
- Receipt lines 8–22 and 24–32 cut off mid-line. For example, line 9 ends `the bytes row 8 prov`, line 16 ends `all {len(PKG_FILES)} b`, and line 21 ends `dir build, in pl`. These are the receipt's actual contents, not terminal display truncation: the numbered raw `rg` read shows the same endings.
- The correction table at canonical lines 204–208 groups files/functions but supplies no per-hit `updated` or `confirmed-consistent` mapping. Lines 217–219 give sweep descriptions and `11 sites found, 11 updated, 0 confirmed consistent`; PR-6 explicitly says a bare count is not a disposition.

The sole reason for refusing this round is this **pre-verdict census precondition**. It is not an expansion of the approved design or a request for additional product scope.

### Checklist Results

| Check | Result | Procedure / observer | Exit | Evidence |
|---|---|---|---|---|
| PR-6 correction census | fail | Read the complete named receipt and correction section; compare raw inventory and per-hit dispositions to protocol PR-6; gpt-6.1-sol | null | Truncated hit text, four count-only historical hits, aggregate correction counts without per-hit dispositions. |
| PR-2 not-started status | pass | Read canonical task.md status cells and git status; gpt-6.1-sol | null | Draft; 20 unchecked task rows; no implementation completion claimed. |
| PR-1/3/4/5/7/8/9; DR-1–8 | n/a this round | Stopped by PR-6 | null | Round-1 results retained above; corrected-content reassessment not performed. |
| plan_checks.py static | n/a; not_run | PR-6 stop | null | No fresh output; the round-1 and author-reported outputs above are historical only. |
| plan_checks.py selftest | n/a; not_run | PR-6 stop | null | No fresh output; no verifier run claimed. |

```json
{"schema_version":"evidence.v1","check_id":"s31b-r2-pr6-census","procedure":"Read all 32 lines of C:/Temp/av-kit/census-s31b-r1-f1.txt with numbered unfiltered rg output and the complete canonical Corrections Applied section (lines 200-219); compare with plan-critical-review.md PR-6 and its procedural verdict exception.","observer":"gpt-6.1-sol","cwd":"P:/av-kit","scope":"round-2 correction-review precondition","phase":"planning","exit_code":null,"result":"fail","tested_state":"main 4a97483669332de67abd434ccd6c2f073cfd6316 plus current uncommitted correction log and named receipt","output":"Receipt contains count-only historical hits and lines ending mid-word (for example 'bytes row 8 prov'); correction log contains only aggregate '11 sites found, 11 updated' rather than a disposition per file:line. PR-6 requires changes_required before corrected-content review.","fresh":true}
```

### Commands executed in round 2

All shell processes used `rtk proxy`, all-stream receipts under `C:/Temp/av-kit/`, an immediately captured child exit, and a completed-receipt read. File reads are read evidence only.

- `rtk proxy powershell -NoProfile -Command "Get-Content ..."` reads loaded the protocol, terminal-preflight skill/output policy, AGENTS, GUARDRAILS, PROFILE, template, canonical rolling report, focus/known issues, harness context, reviewer role, verdict schema, completion-preflight skill, census receipt and canonical task. All exited **0**. UTF-8 reads were used for the report and project context; no secrets were included.
- `rtk proxy rg -n '^' C:/Temp/av-kit/census-s31b-r1-f1.txt` — **0**; all 32 lines inspected, including count-only and truncated entries quoted above.
- `rtk proxy rg -n -A 50 '^## Corrections Applied' .agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md` — **0**; lines 200–219, no per-hit disposition table.
- `rtk proxy rg -n -A 9 -B 3 'pre-verdict|procedural exception|Materiality Gate|No nearby-mutation' .agent/workflows/plan-critical-review.md` — **0**; PR-6 and the exception require stopping before corrected-content review.
- `rtk proxy git status --short` — **0**; eight entries as described above; Git's ignore-config permission warnings retained.
- `rtk proxy git log -1 --format=%H%n%D` — **0**; HEAD/main identity quoted above.
- A task-state `rg` expression initially matched no rows (**1**); task.md was then read directly (**0**). The empty search was not used to establish readiness.
- A lightweight memory-registry search (**0**) found no relevant Session 31b correction evidence; no memory-derived project fact was used.
- Report assembly/readback below preserves the historical body and correction section verbatim, updating only the live frontmatter to round 2. No project validator was invoked.

### Answers to Q1–Q10

These retain the prior answers without reopening approved design; they are **not** fresh corrected-code verification.

| Question | Round-2 answer |
|---|---|
| Q1 TEST_AMENDMENTS | **TA-1–TA-3 remain explicitly approved** as the minimal source-backed amendments reviewed in round 1. |
| Q2 D-56 / MEU-92 | Prior approval of the proposed esbuild bundle, createRequire banner and metafile licences remains. If Mat declines D-56, row 0 must stop for correction/re-review; a reduced MEU-71 plan cannot claim this loop's full goal. |
| Q3 ENTRY_GUARD | Retain round-1 realpath/junction analysis and distinction between assertion Red and tolerated new-module Red; no new launch was observed. |
| Q4 MCP_LAUNCH | Retain prior app-executable/ELECTRON_RUN_AS_NODE launch approval; packaged-proof freshness is unverified this round. |
| Q5 TOKEN_BOUNDARY | Retain prior token-free prompt/IPC assessment and server-side AVKIT_APP_DATA lookup. No secret was opened. |
| Q6 validation scripts | **Not rechecked.** This includes all requested PKG_FILES/identity/result/current/floors negatives and whether fresh npm ci/mcp-bundle invalidates a sound proof. |
| Q7 assertion Red | Retain the prior import partition/NEW_MODULE_FILES approval; actual tests remain future execution evidence. |
| Q8 Claude Code parsing | Retain prior recorded-help analysis; no registration command executed. |
| Q9 spawn tests | Retain prior design feasibility and explicit child/deadline/cleanup requirements; no Windows runtime certification. |
| Q10 fixtures/audit | Retain prior eleven-fixture/quoting analysis and scope-based audit skip approval. The author's wording correction is recorded above but not substantively rechecked after PR-6 failed. |

### Verdict and follow-up actions

**changes_required**, solely under **PR-6's pre-verdict procedural exception**. F1 is `still_open` pending a substantive recheck; no regression or new substantive defect is asserted.

1. Author supplies a complete, unfiltered raw census with every hit and an accompanying correction-log row for every `file:line`, marked `updated` or `confirmed-consistent` with its reason. Historical quotations may be confirmed consistent; they still need to be inventoried.
2. Resume the independent recheck within this same loop and ledger history, focusing on the requested stale-evidence negatives and fresh-rebundle compatibility. Do not reset the round cap.
3. Dispatcher copies this cumulative report from **C:/Temp/av-kit/dispatch/s31b-plan-review-report.md** to the canonical rolling review verbatim. This reviewer does not write the checkout or authorize execution.

Residual uncertainty: R1/R2/R3 remain unexamined this round. The precondition failure is not evidence against the corrected product design. The explicit dispatch write scope and JSON response requirements supersede local canonical-write/timestamp output instructions. Completion-preflight was consulted; execution remains unauthorized and unstarted, so its unchecked-row execution-continuation instruction does not authorize product work.

---

## Corrections Applied — round 2 (census) — 2026-10-16 (author: Claude Code, Opus 5.5)

Verdict is set to `corrections_applied`. This section answers the round-2 PR-6 refusal. **No product or plan design changed after round 2.** The only changes are this census evidence and the round-3 prompt. The round-1 census had two defects: it cut hit text at 160 characters (`cut -c1-160`) and swept without `--hidden`, so `.agent/` went unsearched. The census below fixes both.

**Receipts**
- `C:/Temp/av-kit/census-s31b-r2-f1.txt` is unfiltered: `rg -F -n --hidden -g !.git` over all of `P:/av-kit` with default `.gitignore` rules, full line text, each variant's rg exit code, and every hit as `file:line<TAB>text`.
- `C:/Temp/av-kit/census-s31b-r2-f1.json` holds the same hits in machine-readable form.
- `C:/Temp/av-kit/census-s31b-r2-dispositions.md` is the table below, generated from the JSON. The generator refuses to emit if any site lacks a disposition.
- The census ran after the round-3 prompt edit and before this section was written. This section's own mentions of the variants are self-references and are not inventoried.

**Variants (22).**
- Old values (11): `pkg_result_passed`, "a passing `pkg-probe-result.json`", "rewrites the committed baseline", "packaged probe passed", `s31b-pkg-probe.v1`, `$r.passed`, `bundle_sha256`, `packaged_sha256`, `<bundle.mjs> <packaged.mjs>`, `'mcp-server/bundle/index.mjs', $entry`, "missing or not passed (row 8)".
- New values (9): `PKG_EVIDENCE`, `pkg-current`, `pkg_evidence_errors`, `PKG_FILES`, `s31b-pkg-probe.v2`, `identity_errors`, `pkg_identity`, `_selftest_pkg_evidence`, "audits tool surfaces".
- Consumers of the proof (2): `pkg-probe-result`, `pkg-result`.
- Old-value hits outside this rolling review: **0**. Each of the five old values with no hits anywhere (`bundle_sha256`, `packaged_sha256`, the four-argument usage, the four-argument call, the old gate92 message) returned rg exit 1.

**Per-site dispositions (107 hits at 68 sites)**

| # | Site (file:line) | Variants hit | Disposition | Reason |
|---|---|---|---|---|
| 1 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:42` | `pkg_result_passed` | confirmed-consistent | round-1 reviewer report, kept verbatim (rolling report); quotes pre-correction code |
| 2 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:47` | `pkg_result_passed`, `$r.passed` | confirmed-consistent | round-1 reviewer report, kept verbatim (rolling report); quotes pre-correction code |
| 3 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:97` | `pkg_result_passed` | confirmed-consistent | round-1 reviewer report, kept verbatim (rolling report); quotes pre-correction code |
| 4 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:155` | `pkg-result` | confirmed-consistent | round-1 reviewer report, kept verbatim (rolling report); quotes pre-correction code |
| 5 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:206` | `pkg_result_passed`, `$r.passed`, `PKG_EVIDENCE`, `pkg-current`, `pkg_evidence_errors`, `PKG_FILES`, `s31b-pkg-probe.v2`, `identity_errors`, `pkg_identity`, `pkg-probe-result`, `pkg-result` | confirmed-consistent | round-1 Corrections Applied log, kept verbatim; names old values as replaced |
| 6 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:207` | `_selftest_pkg_evidence` | confirmed-consistent | round-1 Corrections Applied log, kept verbatim; names old values as replaced |
| 7 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:208` | `rewrites the committed baseline` | confirmed-consistent | round-1 Corrections Applied log, kept verbatim; names old values as replaced |
| 8 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:217` | `pkg_result_passed`, `a passing `pkg-probe-result.json``, `rewrites the committed baseline`, `packaged probe passed`, `s31b-pkg-probe.v1`, `$r.passed`, `PKG_EVIDENCE`, `pkg-current`, `pkg-probe-result`, `pkg-result` | confirmed-consistent | round-1 Corrections Applied log, kept verbatim; names old values as replaced |
| 9 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:257` | `pkg_result_passed`, `$r.passed` | confirmed-consistent | round-2 reviewer recheck, kept verbatim; quotes the round-1 receipt |
| 10 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:258` | `PKG_FILES` | confirmed-consistent | round-2 reviewer recheck, kept verbatim; quotes the round-1 receipt |
| 11 | `.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-plan-critical-review.md:302` | `PKG_FILES` | confirmed-consistent | round-2 reviewer recheck, kept verbatim; quotes the round-1 receipt |
| 12 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md:90` | `pkg-probe-result` | confirmed-consistent | WP-3 output names the result file; its binding is the PKG_EVIDENCE row |
| 13 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md:168` | `pkg-probe-result` | confirmed-consistent | producer contract; still writes pkg-probe-result.json, whose v2 content the PKG_EVIDENCE row defines |
| 14 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md:169` | `PKG_EVIDENCE`, `pkg-current`, `PKG_FILES`, `s31b-pkg-probe.v2`, `pkg-probe-result` | updated | new contract row (F1) |
| 15 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md:171` | `PKG_EVIDENCE`, `pkg-probe-result` | updated | AC-92.4 needs a current proof, not a passing one (F1) |
| 16 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md:372` | `PKG_EVIDENCE`, `pkg-current`, `audits tool surfaces` | updated | stage list gains pkg-current (F1); mcp-audit skip reason corrected (Q10 note) |
| 17 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md:558` | `PKG_EVIDENCE` | updated | D-84 binds the proof to file hashes (F1) |
| 18 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md:628` | `PKG_EVIDENCE`, `pkg-current` | updated | names the pkg-current re-check (F1) |
| 19 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:5` | `pkg-result` | confirmed-consistent | module docstring: pkg-result is still the only writer; pkg-current writes nothing |
| 20 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:23` | `pkg-result` | updated | usage: two arguments; the files come from PKG_FILES |
| 21 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:24` | `pkg-current` | updated | usage: new command |
| 22 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:50` | `pkg-probe-result` | confirmed-consistent | result path unchanged |
| 23 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:51` | `PKG_EVIDENCE` | updated | comment for the new bound-file set |
| 24 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:53` | `PKG_FILES` | updated | new bound-file set (10 files) |
| 25 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:174` | `pkg-probe-result` | confirmed-consistent | runtime-AC docstring; the oracle behind it is now pkg_evidence_errors (floors) |
| 26 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:352` | `pkg_evidence_errors`, `PKG_FILES` | updated | replaces pkg_result_passed (F1) |
| 27 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:353` | `PKG_EVIDENCE` | updated | docstring of the new oracle |
| 28 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:359` | `identity_errors` | updated | absent identity (v1 shape) refuses every file |
| 29 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:382` | `pkg_evidence_errors` | updated | floors uses the new oracle (F1) |
| 30 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:464` | `pkg_identity` | updated | new hashing helper |
| 31 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:468` | `identity_errors` | updated | new missing/changed comparison |
| 32 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:479` | `PKG_FILES` | updated | two-argument writer bound to PKG_FILES |
| 33 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:481` | `pkg_identity` | updated | writer records identity |
| 34 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:484` | `s31b-pkg-probe.v2` | updated | schema bump v1 -> v2 |
| 35 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:504` | `pkg_evidence_errors` | updated | pkg_current body |
| 36 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:506` | `PKG_EVIDENCE` | updated | pkg_current failure text |
| 37 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:507` | `PKG_EVIDENCE`, `PKG_FILES` | updated | pkg_current pass text |
| 38 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:571` | `pkg-current`, `pkg-result` | updated | known-command set gains pkg-current |
| 39 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:821` | `pkg-probe-result` | confirmed-consistent | scope selftest: the result file is still an allowed plan-folder output |
| 40 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:841` | `_selftest_pkg_evidence` | updated | selftest calls the new negatives |
| 41 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:845` | `_selftest_pkg_evidence` | updated | new negatives |
| 42 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:846` | `PKG_EVIDENCE` | updated | docstring of the new negatives |
| 43 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:851` | `PKG_FILES` | updated | negatives mirror the real bound-file keys in a temp dir |
| 44 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:859` | `pkg-probe-result` | updated | negatives write a temp result, never the plan's |
| 45 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:861` | `pkg_evidence_errors` | updated | negative assertion (fresh / missing / changed / v1 shape) |
| 46 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:863` | `pkg_evidence_errors` | updated | negative assertion (fresh / missing / changed / v1 shape) |
| 47 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:865` | `pkg_evidence_errors` | updated | negative assertion (fresh / missing / changed / v1 shape) |
| 48 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:867` | `pkg_evidence_errors` | updated | negative assertion (fresh / missing / changed / v1 shape) |
| 49 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:870` | `pkg_evidence_errors` | updated | negative assertion (fresh / missing / changed / v1 shape) |
| 50 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:873` | `pkg_evidence_errors` | updated | negative assertion (fresh / missing / changed / v1 shape) |
| 51 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:895` | `pkg-result` | updated | dispatch: two arguments |
| 52 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py:896` | `pkg-current` | updated | dispatch: new command |
| 53 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/review-prompt-plan.md:7` | `PKG_EVIDENCE` | updated | round-3 prompt history line |
| 54 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/review-prompt-plan.md:24` | `PKG_FILES`, `identity_errors`, `pkg_identity` | updated | round-3 prompt focus |
| 55 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/review-prompt-plan.md:25` | `pkg_evidence_errors`, `_selftest_pkg_evidence` | updated | round-3 prompt focus |
| 56 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/review-prompt-plan.md:26` | `PKG_EVIDENCE`, `pkg-current` | updated | round-3 prompt focus |
| 57 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/review-prompt-plan.md:96` | `pkg-probe-result`, `pkg-result` | confirmed-consistent | round-1 question carried unchanged; its pkg-result subject still exists |
| 58 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/task.md:43` | `pkg-probe-result` | confirmed-consistent | producer row; the -Check pkg-probe it runs now writes the v2 proof |
| 59 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/task.md:44` | `PKG_EVIDENCE`, `pkg-probe-result` | updated | row 9 needs a current proof (F1) |
| 60 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/task.md:48` | `PKG_EVIDENCE` | updated | full gate names PKG_EVIDENCE (F1) |
| 61 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:244` | `pkg-probe-result` | confirmed-consistent | fail-closed: an aborted probe leaves no proof behind |
| 62 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:257` | `PKG_EVIDENCE`, `pkg-current` | updated | comment for the new writer call |
| 63 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:258` | `pkg-result` | updated | two-argument call |
| 64 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:268` | `PKG_EVIDENCE` | updated | gate92 comment |
| 65 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:269` | `pkg-current` | updated | gate92 replaces the $r.passed read (F1) |
| 66 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:295` | `audits tool surfaces` | updated | mcp-audit skip reason corrected (Q10 note) |
| 67 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:315` | `PKG_EVIDENCE` | updated | full-gate stage comment |
| 68 | `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1:316` | `pkg-current` | updated | new full-gate stage after gate-mcp-bundle (F1) |

**Author's notes on R2 (fresh install or rebundle staling a sound proof).** These are for the reviewer to verify and are not evidence.
- `npm ci` never writes either lockfile.
- `esbuild` is pinned exactly (`BUNDLE_SCRIPT`), and its output is deterministic for identical inputs.
- `collectLicenses` sorts sections by package name (`BUNDLE_LICENSES`).
- No gate stage writes under `ui/dist/win-unpacked`: `ui-build` writes `ui/out`, and the harness build writes `ui/out-e2e`.
- `Set-Location ui` in `pkg-probe` runs in a child `pwsh`, so `pkg-result` resolves `PKG_FILES` from the worktree root, the same as every other check.
- A source edit after row 8 does change the fresh bundle. That staleness is intended: rerun row 8.

**Commands executed**
- `uv run python <scratchpad>/census_r2.py` → exit 0 (107 hits, 68 sites).
- `uv run python <scratchpad>/dispositions.py` → exit 0 (`sites 68 updated 48 consistent 20 hits 107`).
- `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check static` was re-run after the round-3 prompt edit and exited 0 (`PASS static: 20 rows, 19 -Check names, 19 ACs covered`; `PASS selftest`, including the PKG_EVIDENCE negatives; `PASS task-lint`). Receipt: `C:/Temp/av-kit/s31b-run-static.txt`. plan_checks.py and validate-task.ps1 are byte-unchanged since round 1's corrections. No build, test or package manager ran.

Blast-radius census: 6 values changed, 22 variants swept, 68 sites found, 48 updated, 20 confirmed consistent.


---

## Round 3 Recheck — 2026-10-16

**Verdict: approved. Current findings: 0; blocking findings: 0.** PR-6 now passes, and the substantive recheck closes F1. Earlier verdicts, findings and correction logs above are historical and remain verbatim; this section supersedes their current-status conclusions. The structured round-3 verdict therefore has an empty findings array.

### Intent Anchor

> Session 31b delivers MEU-71 (a per-client MCP setup prompt that the Settings MCP card shows and copies, with no token in any block and a fixed `mcp-server` entry guard) and, under grouping D-56, MEU-92 (a self-contained `esbuild` bundle of the MCP server that the packaged app ships and `MCP_ENTRY_PROBE` proves starts from a built `win-unpacked` tree).

**Intent achieved: yes, at plan-review level.** Executing the corrected plan would deliver that objective. Product implementation and runtime verification remain unstarted; approval does not certify an already working bundle or GUI.

### Prior-finding recheck / current findings

| Finding | Round-1 status | Round-2 status | Round-3 status | Evidence |
|---|---|---|---|---|
| F1 — High, blocking control-defeat; subject `committable-tooling`; mechanism `task-row-completion-predicate`; stale packaged evidence can satisfy AC-92.4 | open | still_open; corrected content not examined because PR-6 failed | **fixed** | `plan_checks.py:53–64,352–359,382–385,460–507,845–876`; `validate-task.ps1:240–269,313–316,354–358`; plan `:169,171,372,558,628`; task `:44,48`. Removed entry, changed bundle/config and identity-free proof are rejected by the shared consumer; selftest exit 0. |

**New findings: none.** No surviving round-1 delivery finding or regression was identified. The former Q10 wording note is also corrected at plan `:372` and validator `:295`. Recommendation for F1: retain this implementation and require a fresh row 8 whenever the bound identity changes. No further plan-correction round is requested.

### Scope and PR-6 prerequisite

Independent OpenAI review of the Anthropic-authored, unstarted plan in **P:/av-kit**, HEAD **4a97483669332de67abd434ccd6c2f073cfd6316**. Primary targets were read in full: `implementation-plan.md`, `task.md`, `plan_checks.py`, `validate-task.ps1`. Basenames below refer to `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/`. The specified triage/plan-time diff, packaging/server source and configuration, relevant canon, recorded CLI help and approved Session 38 peer were inspected. Existing approved design was retained rather than reopened.

PR-6 was evaluated **before** corrected-content review. Compared the raw text receipt with its JSON copy and the correction table in the canonical rolling report:

- **22 variant sections, 107 hits, 68 distinct file:line sites.** Every JSON hit has its complete `file:line<TAB>text` in the raw receipt. No truncated hit or missing raw record was found.
- **68 dispositions:** 48 `updated`, 20 `confirmed-consistent`; no missing or extra site. Reasons distinguish historical quotations from live consumers. Every recorded hit text still equals the current line at its recorded site.
- Each variant records rg exit 0 or 1. The five zero-hit old variants explicitly record exit 1. The receipt declares `--hidden` and includes `.agent/` hits. The newly appended census section's own self-references were explicitly excluded at capture time; that is consistent with its recorded capture order.

**PR-6 passes.** Both the complete raw inventory and the per-site interpretation are now available. The prior round's procedural refusal is resolved.

Mat's D-56 acceptance, ledger continuation/budget ruling and worktree/commit-plan approval are taken from this trusted user request. The on-disk grouping still says `open`; task row 0 expressly records the ruling before prerequisites run. This is scheduled work, not an unresolved request to Mat. No execution worktree or either MEU handoff exists; all 20 task rows are unchecked.

### Substantive recheck: R1–R3

**R1 — packaged evidence and its consumers.** `pkg_result` hashes ten named files, refuses missing inputs through `byte_equal`, requires both source/package entry and licence pairs to match, requires nonempty packaged notices and both successful probe records, and writes the v2 identity. `pkg_evidence_errors` requires an existing result, `passed is True`, and current hashes for every `PKG_FILES` key. `_sha` returns an empty value for a missing file; `identity_errors` checks absence before equality, so absent files cannot satisfy one another.

| Adversary after a passing row 8 | Observed static result | Verification |
|---|---|---|
| Remove packaged `index.mjs` | `packaged_entry` hashes to empty; consumer returns `missing` | Selftest `:862–865` exercises rejection and restored-file recovery. |
| Rebuild bundle with different bytes | Source `bundle` hash differs from recorded identity | Selftest `:866–868`; `gate92` and full gate rebuild before checking. A byte-identical rebuild correctly remains valid. |
| Change `ui/electron-builder.yml` | Bound config hash differs | Selftest `:869–870`. |
| Change either lockfile or package manifest | Corresponding key differs in the same unconditional ten-file loop | Static trace `:60–63,468–475`; no separate live lockfile mutation was performed. |
| Supply old `{passed: true}` proof without identity | All ten recorded hashes are absent; every current file is rejected | Selftest `:871–873`. |
| Package an entry different from the source bundle | Writer returns 1 and records `passed: false` | Selftest `:874–876`; expected diagnostic is reproduced below. |

The call chain reaches **all three completion surfaces**: row 9 runs `gate92` → rebuild bundle → `pkg-current`; H1-2 runs `gate-mcp-bundle` → `gate-pkg-current`, with stage failure stopping the gate; final `floors` again invokes `pkg_evidence_errors` for runtime AC-92.4. None of those paths can pass on the requested stale/absent-file examples. The plan's PKG_EVIDENCE, COUNT_FLOORS, full-gate description, D-84 and task rows 9/H1-2 agree with this wiring.

**Bound-file set:** appropriate for this MCP startup proof. It covers the actual executable, shipped entry/notices, fresh source entry/notices, packaging configuration, and both dependency manifests/lockfiles. Entry/guard/source/build-script changes that affect bundled execution are exposed by the required fresh bundle; licence changes are exposed by the fresh notices. UI `out/`, renderer code, backend/FFmpeg assets, mtimes, install caches and Git commit identity are not needed to decide whether those same MCP bytes start under that executable. The whole UI/application contract still has its separate full gate. This is deliberately a scoped MCP proof, not a digest of every installer resource or arbitrary external environment change. Requiring UI dependency files is conservative and appropriate because they select Electron/electron-builder; their edits intentionally require repackaging.

**R2 — fresh-install / rebuild compatibility:** no inherent false-staleness regression found. The installed npm `ci.js:52–58` supplies `save: false` expressly to avoid modifying manifests or lockfiles; its lock validation precedes installation (`:81–88`). Neither project declares a root install/prepare lifecycle script that rewrites these bound inputs. Reinstalling `node_modules` and Electron's development binary does not replace the already packaged `win-unpacked/av-kit.exe`. The planned esbuild inputs/options have no timestamp/random field, use the exact version/lock graph and the same worktree paths; notices have an explicit package-name sort. Thus ordinary identical-input rebundling should reproduce the two bound bundle outputs. No bitwise reproducibility experiment was run: the build scripts are future deliverables. If execution observes changed bytes, the gate correctly refuses and requires investigation or a fresh row 8; do not bypass it.

The full gate writes `ui/out` and `ui/out-e2e`, not `ui/dist/win-unpacked`; row 10 edits docs and does not invalidate the ten inputs. `pkg-builder` changes cwd inside a child `pwsh`, leaving `pkg-result` and later consumers rooted at the worktree. Hashing content instead of mtimes avoids reinstall/build-time-only invalidation.

**R3 — remaining round-1 concerns:** F1 was the sole blocker; it is now fixed. The TA amendments, entry/launch/token design and D-56 bundle proposal remain approved. The optional audit-rationale wording has been corrected. No new materially different delivery failure was found; no additional predicate-hardening or ceremony finding is raised.

### Answers to Q1–Q10

| Question | Round-3 answer |
|---|---|
| Q1 TEST_AMENDMENTS | **TA-1, TA-2 and TA-3 are explicitly approved as written.** Channel-count/census and audit-inventory additions are minimal consequences of the new strict channel/action; opening Advanced preserves the old copy/pin assertions. No other expectation amendment is authorized. |
| Q2 D-56 / MEU-92 | Retain approval: self-contained ESM with createRequire and metafile notices is appropriately scoped and avoids another shipped node_modules tree. Hermetic and packaged startup remain required. Mat has accepted D-56. Counterfactually, decline is handled safely by row 0's stop/correct/re-review path; a reduced plan cannot claim this two-MEU Goal. |
| Q3 ENTRY_GUARD | Realpath identity supports plain dist, bundled index.mjs and junction/symlink launch, while imported/missing files fail closed. The old argv suffix guard misses `/resources/mcp-server/index.js`, making AC-71.9's initialize failure real by static trace. AC-71.8 instead has the declared new-module import tolerance. No spawn occurred here. |
| Q4 MCP_LAUNCH | Absolute app executable plus ELECTRON_RUN_AS_NODE and one absolute script argument is coherent in dev/package modes. AC-71.10 must use the real binary, bypassing the unit-test electron alias, and assert first-line JSON-RPC; AC-92.4 proves the packaged executable. FUSE_PIN is supplementary configuration coverage. F1's freshness gap is closed. |
| Q5 TOKEN_BOUNDARY | New prompt builder/IPC/copy path needs only launch metadata and appData, never readMcpToken. AVKIT_APP_DATA directs each same-user client to the server's own descriptor/token lookup. Synthetic fixture tokens are valid negative oracles. Existing Advanced main-side copy intentionally puts the token on the clipboard and returns only an acknowledgement; it is not the new prompt payload. No live secret/config was opened. |
| Q6 validation | The merged-project Red checks, expect-based Electron Red, AC-name/count floors and whole-repository source allowlist retain their prior approval. Packaged AC coverage now uses the current ten-file identity. Missing required AC names cannot pass ordinary floors; unrelated unlisted source/config changes fail scope. Report names cannot establish assertion semantics: inspect decisive Red locations during execution. This known limit does not reopen the already reviewed parser surfaces. |
| Q7 assertion Red | Existing-module IPC/Settings and builtins-only spawn/bundle tests can collect before implementation and fail on assertions. NEW_MODULE_FILES remains the correct four MEU-71 files plus MEU-92 bundle-licenses. Guard missing values with assertions before dereferencing them. Future test code/Red output still needs execution review. |
| Q8 Claude Code parsing | Recorded help `:14,25,29–30` explicitly demonstrates name then variadic -e then `--` then command. Repeated env pairs plus explicit scope and the separator are sound. No client-registration command ran. |
| Q9 spawn determinism | Feasible at design level, not runtime-certified: junctions, isolated app data/fake backend, assertion on early exit/deadline, and kill/await/close/remove teardown remain required. Clear inherited token/base overrides in the no-token fixture. The Python packaged probe has bounded normal-path polling/kill/communicate; unexpected process/pipe errors fail rather than certify startup. |
| Q10 goldens / quoting / audit | Eleven fixtures remains correct (seven user, four project). JSON/TOML escaping and Claude Code double quotes cover the specified Windows paths; PATH_QUOTE_ERROR rejects shell-sensitive quote/dollar/backtick input. Expected fixtures must remain independent of the builder. Tool-surface audit skip remains justified; its rationale now accurately distinguishes tool snapshots from server instructions. |

### Checklist results

Manual observations below were performed by **gpt-6.1-sol**, with **exit_code null**. They evaluate the plan, not completed product behavior.

| Check | Result | Observed procedure / evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Read both complete files; both MEUs, row order, PKG_EVIDENCE and H1/H2 boundaries agree. |
| PR-2 Unstarted state | pass | Read all task rows and inventory worktree/handoff paths: 20/20 unchecked; worktree and both handoffs absent. |
| PR-3 Task contract | pass | Read every task row and validator branch; static reports 20 rows, 19 check names, 19 ACs. |
| PR-4 Validation realism | pass | Trace F1's producer → current-proof consumers and failure propagation; all requested stale-proof cases reject. |
| PR-5 Sources | pass | Cross-read FIC/source labels, 07/06/05, grouping and known-issue changes; no new unsourced behavior introduced by correction. |
| PR-6 Corrections readiness | pass | Compare raw/JSON/log and current file lines: 107 complete hits, 68 dispositions, zero missing/extra/stale records. |
| PR-7 Scope discipline | pass | Recheck Out of Scope bases and row-0 declined-D-56 stop; no required packaged dependency work is silently deferred. |
| PR-8 Reachability / negatives | pass | Trace row 8 producer through row 9 and full gate/floors; permitted selftest exercises material missing/changed/mismatched proof negatives. |
| PR-9 Repeated literals | pass | Named-contract sweep of the four live targets; no competing material packaged-evidence rule survives. |
| DR-1 Claim/state | pass | Inspect complete specified Git diff and corrected files; no completed implementation claim. |
| DR-2 Residual old terms | pass | Read dispositioned historical hits and live-target sweep; old proof logic is absent from active consumers. |
| DR-3 Downstream refs | pass | Plan-time MEU-71 execution_plan/rendered state and grouping path align; remaining hub updates have explicit row-0/10 owners. |
| DR-4 Robustness | pass | Shared identity oracle defeats F1 at every completion surface; no required new behavior is bypassed. |
| DR-5 Auditability | pass | Full raw census, individual dispositions, line-level traces and exact allowed-verifier output below. |
| DR-6 Architecture | pass | Prompt remains in main with strict preload IPC; server owns token reads; bundling changes no tool/API surface. |
| DR-7 Freshness | pass | Reproduce static/selftest now and compare census hit text with current files; no product-suite receipt is promoted to current runtime evidence. |
| DR-8 Completion / uncertainty | pass | Approval is of the plan. Runtime, test implementation, package interop and Mat's look check remain execution obligations. |

AV-1: n/a for future product Red/Green; verifier negatives observed. AV-2/AV-3/AV-4: pass at design level (explicit oracles; no prescribed assertion bypass/skip). AV-5: n/a, no completed product deliverable claimed. AV-6: pass, source-backed FIC retained.

### Commands executed and durable evidence

All shell commands used RTK, receipts under C:/Temp/av-kit and preserved exits. Cwd was P:/av-kit. No project tests/builds, npm/uv, generator, validator PowerShell check, Electron or client-registration command was executed.

| Command / observation | Exit | Result |
|---|---|---|
| `rtk proxy python -X utf8 docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py static` | 0 | `PASS static: 20 rows, 19 -Check names, 19 ACs covered` |
| `rtk proxy python -X utf8 docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py selftest` | 0 | Full output below; negative mismatch intentionally prints FAIL before PASS selftest. |
| `rtk proxy git status --short` | 0 | Five modified triage/canon files; untracked canonical rolling review, plan folder and local Claude settings. Settings contents were not opened. Config-access warnings retained. |
| `rtk proxy git log -1 --format="%H %s"` | 0 | HEAD `4a97483669332de67abd434ccd6c2f073cfd6316`. |
| `rtk proxy git diff -- .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md .agent/context/known-issues.yaml .agent/context/meu-registry.md .agent/context/meu-status.yaml docs/BUILD_PLAN.md docs/build-plan/07-distribution.md` | 0 | Complete triage/plan-time diff inspected; docs/BUILD_PLAN.md has no current diff; line-ending warnings retained. |
| Live-target named-contract sweep; exact command below | 0 | Active consumers agree on current proof; complete output retained in s31b-r3-literals.txt. |
| Read-only `rtk proxy python -X utf8 -c` and `rtk proxy pwsh -NoProfile -Command` file/line reads and inventories | 0 on completed reads | Full primary targets, context/protocol/template, peer excerpts, canon and help. Census audit: 22 variants/107 hits/68 dispositions; current-line mismatches 0. Invoked external helpers exist; scheduled worktree/handoffs absent. |

```powershell
rtk proxy rg --hidden -n -e "PKG_EVIDENCE|pkg-current|pkg_result_passed|COUNT_FLOORS|s31b-pkg-probe.v1|s31b-pkg-probe.v2|packaged probe passed|rewrites the committed baseline" docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/task.md docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 *> C:/Temp/av-kit/s31b-r3-literals.txt; $readCode=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s31b-r3-literals.txt; exit $readCode
```

The census comparison and F1/R2 code traces are manual/static evidence, not a newly run correction generator or product test. The Python read scripts only inspected files and compared inventories. A lightweight memory-registry search supplied no relevant Session 31b fact used in the verdict.

Recoverable review-tool diagnostics: the initial nested PowerShell wrapper expanded its exit variable incorrectly after writing the bootstrap read receipt; later reads used corrected single-quoted wrapper text. One initial Python read hit cp1252 UnicodeEncodeError (exit 1); its UTF-8 retry succeeded (exit 0). One orchestration-cell string failed parsing before starting a shell and was corrected. None is product verification evidence or grounds for approval. Full receipts retain the diagnostics.

```text
PASS PKG_PROBE: bundle and LICENSES.txt byte-equal in win-unpacked (923fe53966c6), both probes started; proof bound to 10 files
FAIL: PKG_PROBE: missing [], byte_equal False, licences True, in-place started, hermetic started
PASS selftest
```

The selftest uses synthetic temp files/probe records. Its first line does **not** mean that this review built or launched a packaged app. The second line is the intentionally rejected unequal-entry case.

```json
{"schema_version":"evidence.v1","check_id":"s31b-r3-static","command":"rtk proxy python -X utf8 docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py static","cwd":"P:/av-kit","scope":"plan/task/validator static contract","phase":"planning","exit_code":0,"result":"pass","tested_state":"HEAD 4a97483669332de67abd434ccd6c2f073cfd6316 plus directly read uncommitted Session 31b plan-time files, ledger round 3","output":"PASS static: 20 rows, 19 -Check names, 19 ACs covered","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-r3-selftest","command":"rtk proxy python -X utf8 docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py selftest","cwd":"P:/av-kit","scope":"plan-local synthetic verifier cases including PKG_EVIDENCE","phase":"planning","exit_code":0,"result":"pass","tested_state":"current plan_checks.py read in full, ledger round 3","output":"PASS PKG_PROBE: bundle and LICENSES.txt byte-equal in win-unpacked (923fe53966c6), both probes started; proof bound to 10 files\nFAIL: PKG_PROBE: missing [], byte_equal False, licences True, in-place started, hermetic started\nPASS selftest","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-r3-census-and-proof-trace","procedure":"Compare every raw census hit with its JSON text, disposition row and current file line, then trace pkg_result, pkg_evidence_errors, identity_errors, floors and both PowerShell completion call chains; inspect installed npm ci and declared build outputs for fresh-install compatibility.","observer":"gpt-6.1-sol","cwd":"P:/av-kit","scope":"PR-6 and substantive R1/R2/R3 recheck","phase":"planning","exit_code":null,"result":"pass","tested_state":"current Session 31b primary targets and cumulative correction log in main checkout, ledger round 3","output":"22 variants, 107 full hits, 68 dispositions (48 updated, 20 consistent), zero missing/extra/stale census sites. F1 fixed at all three consumers. Lockfile/config changes and absent identity fail the shared hash comparison; no inherent unchanged-input rebuild invalidation found.","fresh":true}
```

### Verdict and follow-up actions

**approved** — PR-6 is satisfied and F1 is fixed. **TA-1–TA-3 remain explicitly approved.** No open finding blocks the corrected plan's registered Goal. This is the final review round; no review-loop reset or further plan round is requested.

1. Dispatcher validates this round-3 verdict against the existing target/intent/ledger and copies the complete report **verbatim** from **C:/Temp/av-kit/dispatch/s31b-plan-review-report.md** to the canonical rolling review path. Frontmatter describes round 3; all earlier body sections remain historical.
2. Follow Mat's already approved commit/worktree plan and the execution gate. Row 0 records the accepted D-56 ruling and registers MEU-92. This reviewer creates no worktree, commit or product edit.
3. Execute the preserved TDD/runtime obligations: independent golden expectations, intended assertion Red, Windows child cleanup, real Electron, hermetic bundle, fresh packaged probe, full gate and MCP_PROMPT_LOOK. A changed bound identity requires a fresh row 8 before completion can pass.

Residual uncertainty is limited to unexecuted implementation/runtime behavior and future build reproducibility, as appropriate for this static plan review. The receipt-only write restriction and JSON final-response requirement take precedence over local canonical-write/timestamp instructions. Completion-preflight was consulted and canonical task readiness was inspected; its execution-continuation rule does not authorize this independent reviewer to implement the unchecked plan.


Closeout readback: exact ten-key frontmatter verified; original rolling body preserved byte-for-byte (55,259 bytes); three new evidence.v1 records parse; final git status --short (exit 0) is byte-identical to the initial receipt. No repository file was written by this review.
