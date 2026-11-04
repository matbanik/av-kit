---
review_mode: plan
target_plan: docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md
verdict: approved
findings_count: 0
round: 3
date: 2026-08-24
agent: GPT-5.6-sol (Codex)
template_version: 2.1
requested_verbosity: standard
---

# Critical Review: p7-distribution

> **Review Mode**: `plan`
> **Verdict**: `approved`

---

## Intent Anchor

Executing this plan is supposed to produce a secret-free, localhost-only PyInstaller onedir backend and an NSIS package whose resources-root `avkit-backend`, `ffmpeg`, and `mcp-server` payloads match Electron's existing production spawn and MCP behavior. In its current form, the plan can close with no NSIS build attempt, an ambiguous onedir source, and an FFmpeg wire that is not necessarily reachable from the installed layout, so it would not reliably deliver that objective.

## Scope

**Primary targets**:

- `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md`
- `docs/execution/plans/2026-08-24-p7-distribution/task.md`
- `docs/execution/plans/2026-08-24-p7-distribution/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-24-p7-distribution/assert-handoff-markers.ps1`

**Canon sampled**:

- `docs/build-plan/07-distribution.md`
- `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` (Progress, Session 12, and open decision 8)
- `packages/api/src/avkit_api/cli.py`
- `packages/api/src/avkit_api/wiring.py`
- `packages/infrastructure/src/avkit_infra/media/adapter.py`
- `ui/src/main/python-manager.ts`
- `ui/src/main/index.ts` production caller of `packagedBackendPath` / `spawnOwned`
- `ui/src/main/ipc.ts` and the existing focused UI tests

**Review type**: unstarted execution-plan review. **Checklist applied**: PR-1 through PR-9.

No project tests, packaging commands, repository tools, or plan scripts were executed. Static `Get-Content`, `Test-Path`, and `rg` evidence only.

---

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | High | **PR-8 / PR-9 — The NSIS source for the PyInstaller onedir is materially ambiguous.** [r1] `PACK_DIST` is defined as the executable file, while `EXTRA_RESOURCES` says `from: PACK_DIST dir`. Those are different live contracts: copying the executable does not copy the onedir support payload and can leave Electron's `resources/avkit-backend/avkit-backend.exe` target unlaunchable. AC-25.2 checks only the three `to` destinations, so this ambiguity can pass its negative oracle. | `implementation-plan.md:101`, `implementation-plan.md:107`, `implementation-plan.md:197`, `implementation-plan.md:238` | Define separate single owners such as `PACK_DIST_DIR = packaging/dist/avkit-backend` and `PACK_DIST_EXE = PACK_DIST_DIR/avkit-backend.exe`; make `EXTRA_RESOURCES.from` use the directory and add a negative oracle proving the installed backend directory contains the executable plus the onedir support tree at `RESOURCES_BACKEND`. | fixed |
| 2 | High | **PR-4 / PR-8 — The plan never attempts an NSIS build, and row 6 false-passes a missing artifact.** Row 5 runs only Python tests. Row 6 merely searches `ui/dist`; when nothing exists it writes `BLOCKED`, prints `PASS`, and exits 0. No external packaging error is reproduced and no concrete CI follow-up is linked, so this does not satisfy the evidence-gated `[B]` rule. Executing the table can therefore finish without electron-builder ever consuming `BUILD_CONFIG` or `EXTRA_RESOURCES`. This finding does not require a clean-VM install to be a sandbox HARD STOP. | `task.md:48-49`, `implementation-plan.md:246`, `implementation-plan.md:333-346` | Add an exact local UI-build + electron-builder NSIS command before the size check. Permit `[B]` only after that command produces an external dependency/environment error receipt, and name the concrete CI follow-up. Keep the clean-VM install/launch check as the separately allowed `[B]` + CI escape. | fixed |
| 3 | High | **PR-5 / PR-8 — `BUNDLE_WIRE` has no selected production bridge from the installed resources layout to Python.** The named contract calls an undefined `bundled_ffmpeg()`, while AC-25.4 permits either `AVKIT_FFMPEG_BUNDLE` or a packaged-layout resolver. The current Electron production caller forwards only `{ ...process.env }`, the task does not modify that caller, and current `build_services` constructs `FFmpegAdapter` without `bundle_path`. A test can satisfy the environment branch while the shipped backend never receives that variable and cannot find `resources/ffmpeg/ffmpeg.exe`. | `implementation-plan.md:103`, `implementation-plan.md:110`, `implementation-plan.md:240`, `task.md:48`; `ui/src/main/index.ts:169-202`; `packages/api/src/avkit_api/wiring.py:99-142` | Select and source one real bridge: either derive the sibling resources-root FFmpeg path from the packaged backend executable in Python, or have Electron set a named child environment value and include that caller in Files Modified. State the full production chain (`boot`/`cli.main` -> resolver -> `build_services` -> `FFmpegAdapter`) and add a negative oracle with a PATH decoy proving the bundled file wins. | fixed |
| 4 | High | **PR-8 — AC-24.6 proves forbidden labels, not that the actual two secret values stay out of the descriptor.** `SECRET_KEYS` and the negative case catch a `token` key, but a token value placed under any allowed `DESCRIPTOR_KEYS` field would pass both AC-24.6 and the exact-key check in AC-24.7. That is a concrete secret-leak false-pass on a security control. The current implementation correctly discards both arguments, but the planned oracle does not bind that behavior. | `implementation-plan.md:98-99`, `implementation-plan.md:193-194`; `packages/api/src/avkit_api/cli.py:165-197` | Invoke `write_descriptor` with two unique sentinel secret values and assert each sentinel is absent from the returned object serialization and exact file bytes, in addition to checking forbidden key names. Make the negative mutation place a sentinel under an otherwise allowed descriptor key. | fixed |
| 5 | Medium | **PR-4 / PR-8 — The native TypeScript negative oracles for path parity and default MCP omission are not scheduled.** `MEU25_TOUCHED` names `copy-mcp-config.test.ts` as “prove only,” but every MEU-25 gate runs pytest only. The existing MCP test exercises the real `handleIpc` behavior; the existing spawn test does not assert `packagedBackendPath(resourcesPath)`. Thus AC-25.3 and AC-25.8 are described but their production-language observables are absent from the task's executed validation set. | `implementation-plan.md:146`, `implementation-plan.md:239`, `implementation-plan.md:244`, `task.md:48-50`; `ui/tests/unit/dev-spawn.test.ts:31-37`; `ui/tests/unit/copy-mcp-config.test.ts:16-26` | Add an exact focused Vitest command to the Green and MEU-25 gates. Extend the packaged-spawn test with the locked resources-root path and an `extra/` negative; run the existing MCP default-omit test without changing `ipc.ts` unless it exposes a regression. | fixed |
| 6 | Low | **PR-9 — Several named values are restated in `task.md` and the marker script instead of being referenced through one executable owner.** The repeated clusters include the Red prefixes/count 10, `HANDOFF_COUNT = 2` plus both handoff names, and `HUB_NEXT_AFTER = phase-7 complete`. These are clerical today, but they defeat the plan's stated single-statement discipline. | `implementation-plan.md:119-143`, `task.md:44`, `task.md:47`, `task.md:50-51`, `assert-handoff-markers.ps1:3-10` | Keep each literal in one executable owner and make task prose/commands reference that owner; report this cluster once during `/plan-corrections`. | fixed |

No Critical findings were identified.

---

## Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | fail | Scope and sequence align, but task rows do not execute all promised control proofs and do not attempt the NSIS build (`task.md:48-50`). |
| PR-2 Not-started confirmation | pass | All implementation and closeout rows are unchecked; planned product files, tests, MEU handoffs, and implementation-review handoff are absent. `task.md`'s frontmatter `in_progress` denotes the planning workflow, not completed implementation. |
| PR-3 Task contract completeness | pass | Every actionable row supplies task, owner, deliverable, validation, dependencies/context, durable outputs, builder model, and status. `fresh_worker: none` is consistently represented as `compact_continue`/`shared`, and every `builder_model` is `—`. |
| PR-4 Validation realism | fail | Findings 2 and 5 demonstrate missing executable validations and a missing-artifact false-pass. |
| PR-5 Source-backed planning | fail | The environment-variable branch in AC-25.4 is neither selected nor bound to a planned producer; the spec requires the installed bundled path, not a test-only environment branch. |
| PR-6 Handoff/corrections readiness | pass | `HANDOFF_COUNT = 2`, both canonical MEU handoffs, and one rolling implementation-review path are explicit. Round-2+ correction-census rules do not apply to Round 1. |
| PR-7 Scope discipline (C2) | pass | Per `USER_EXPLICIT`, Session 8c is treated as a grouping-level Human-approved insert and is not used to invent or require a p7 MEU. The p7 plan stays on MEU-24 then MEU-25. FastAPI/MCP rewrites and chrome/Settings rewind remain out of scope on cited grouping/canon bases. |
| PR-8 Control reachability/totality | fail | Findings 1-5 show concrete false-passes or dead-end production chains. By contrast, localhost bind, onedir-vs-onefile, resources-root backend destination, probe order, and default MCP omission are directionally correct in the FIC. |
| PR-9 Single-statement discipline | fail | Finding 1 is a materially ambiguous `PACK_DIST` contract; finding 6 is the consolidated clerical repeated-literal cluster. |

### Named Focus Checks

| Focus | Result | Evidence |
|-------|--------|----------|
| `RESOURCES_BACKEND` path lock | pass with Finding 1 dependency | The path is correctly locked to `join(process.resourcesPath, 'avkit-backend', 'avkit-backend.exe')`; the remaining blocker is the ambiguous source copied into that destination. |
| `resources/extra/` diagram treatment | pass | The plan correctly treats `extra/` as conceptual and uses resources-root `to` folders matching current Electron canon. |
| `fresh_worker: none` / builder pin | pass | No `isolated` rows; non-shared rows use `compact_continue`; `builder_model` is `—`. |
| Handoff/hub/grouping lifecycle | pass | `HANDOFF_COUNT = 2`; `HUB_NEXT_AFTER = phase-7 complete`; grouping completion is ordered only in H2 after H1-7 execution approval. |
| create-plan §4A | pass | No new renderer controls are planned, so the GUI element-index skip is correct. |
| Red-oracle artifacts | pass with semantic findings above | Both scripts exist. `assert-red-oracle.ps1` statically enforces ten distinct failed AC IDs for each Python prefix and rejects common collection/config failures; `assert-handoff-markers.ps1` enforces exactly the two named handoffs and all marker names. The scripts were inspected, not executed. |
| Clean-VM escape | pass with Finding 2 distinction | Clean-VM install/launch may remain `[B]` + CI and is not a sandbox HARD STOP. The local NSIS build itself still needs an attempted command and evidence. |

---

## Commands Executed

Only static evidence commands were used:

- Full, line-numbered `Get-Content` reads of all four review targets.
- Full reads of `docs/build-plan/07-distribution.md` and the named production canon; targeted read of grouping Session 12 and the Electron `boot()` caller.
- `Test-Path` checks for target scripts, referenced existing tools/templates, planned-not-yet-created product artifacts, tests, and handoffs.
- `rg` call-site, control-validation, C2, and PR-9 repeated-literal censuses.

Canonical receipts include:

- `C:/Temp/av-kit/plan-review-paths.txt`
- `C:/Temp/av-kit/plan-review-task-scripts.txt`
- `C:/Temp/av-kit/distribution-canon-001-170.txt`
- `C:/Temp/av-kit/distribution-canon-171-end.txt`
- `C:/Temp/av-kit/control-call-sites.txt`
- `C:/Temp/av-kit/control-validation-census.txt`
- `C:/Temp/av-kit/pr9-census.txt`
- `C:/Temp/av-kit/not-started-check.txt`
- `C:/Temp/av-kit/plan-review-pre-edit-guard.txt`

---

## Open Questions / Assumptions

- No human decision is required to correct these findings: the build-plan and existing production paths determine the intended behavior.
- Per the review instruction, no finding asks this plan to adopt or invent a MEU for Session 8c. A current `MEU-27` registry record was observed during the static C2 census, but it is outside this plan's MEU-24/25 scope and does not override the supplied Human-approved grouping basis.
- Clean-VM NSIS acceptance remains an allowed `[B]` + CI follow-up when the environment is unavailable; it is not converted into a sandbox HARD STOP.

---

## Required Follow-up

Route corrections through `/plan-corrections` and resolve Findings 1-6 in the existing plan/task/oracle files. Do not begin implementation until an independent Round 2 review returns `approved`.

## Verdict

`changes_required` — four High findings demonstrate that the current task table can omit the full PyInstaller onedir payload, leave FFmpeg unreachable from the installed layout, leak actual secret values without tripping the oracle, and complete without attempting electron-builder. The correct path lock, no-rewrite scope, two-handoff lifecycle, H2 grouping order, §4A skip, and clean-VM `[B]` policy survive review.

## Residual Risk

After correction, clean-machine install/launch and bundled-FFmpeg availability may still remain CI evidence rather than local sandbox evidence. That residual risk is acceptable only when recorded as the plan's explicit `[B]` + linked CI follow-up; it must not mask a locally unattempted package build.

---

## Corrections Applied — 2026-08-24 (create-plan Step 5b / plan-corrections)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Independent Round 2 must re-score.

**Instruction conflict (flagged, not silently picked):** `plan-corrections.md` HARD STOP says do not auto-chain into `/plan-critical-review`. Driving workflow is `/create-plan` Step 5b, which requires re-dispatch after the census. Re-dispatch proceeds under create-plan.

### Finding dispositions

| # | Change | Files |
|---|--------|-------|
| F1 | Split `PACK_DIST` into `PACK_DIST_DIR` + `PACK_DIST_EXE`. `EXTRA_RESOURCES.from` is the onedir directory. AC-25.2 negative: exe-only copy. | implementation-plan.md; named-sets.json |
| F2 | Row 6 now runs `NSIS_BUILD_CMD` then `NSIS_PACK_CHECK`. Missing artifact is FAIL. `[B]` + `NSIS_PACK_FOLLOWUP` (`NSIS-SANDBOX-PACK` + CI `windows-latest`) only after an external-error build receipt. `CLEAN_VM` is a separate later `[B]`. | task.md:6; assert-nsis-pack.ps1 |
| F3 | Selected `BUNDLE_RESOLVER`: frozen sibling `{exe}/../ffmpeg/ffmpeg.exe`. Chain `cli.main` → `build_services` → `bundled_ffmpeg()` → `FFmpegAdapter`. Rejected Electron `AVKIT_FFMPEG_BUNDLE` as the production bridge. AC-25.5 PATH decoy. | implementation-plan.md AC-25.4/25.5 |
| F4 | AC-24.6 uses `SECRET_SENTINELS` (two unique values) absent from return + file bytes; negative mutates an allowed `DESCRIPTOR_KEYS` field. | implementation-plan.md |
| F5 | `VITEST_MEU25` scheduled on Green, MEU-25 gate, and H1-2. AC-25.3 extends `dev-spawn.test.ts`; AC-25.8 reuses `copy-mcp-config.test.ts`. | task.md:5,7,H1-2 |
| F6 | `named-sets.json` is the executable owner of counts, handoff names, `HUB_NEXT_AFTER`, `PACK_DIST_*`, `SIZE_CAP_BYTES`. Oracles load it (`-Meu 24/25`). SSOT Python loads `HUB_NEXT_AFTER`. | named-sets.json; assert-*.ps1; task.md |

### Blast-radius census (Step 5c)

Index: `C:/Temp/av-kit/census-p7-index.txt`. Unfiltered receipts `C:/Temp/av-kit/census-p7-01.txt` … `census-p7-16.txt`.

| Value | Receipt | Hits | Disposition |
|-------|---------|------|-------------|
| `PACK_DIST` (old bare name) | 01 | substring hits only on `PACK_DIST_DIR` / `PACK_DIST_EXE` / `PACK_DIST_*` | confirmed-consistent |
| `PACK_DIST_DIR` | 02 | definition + EXTRA_RESOURCES + AC-24.10 + AC-25.2 + task 2/5 | updated |
| `PACK_DIST_EXE` | 03 | definition + negatives + smoke AC | updated |
| `from: PACK_DIST dir` | 04 | 0 | updated (gone) |
| `ExpectedCount 10` | 05 | 0 | updated (gone) |
| `-Meu 24` / `-Meu 25` | 06/07 | oracle commands + named set | updated |
| `HUB_NEXT_AFTER` | 08 | SSOT loads from `named-sets.json`; prose does not restate the string | updated |
| `PASS: CLEAN_VM documented` | 09 | 0 | updated (gone) |
| `NSIS_PACK_CHECK` | 10 | WP-25c, lock 4, AC-25.10, task 6 | updated |
| `AVKIT_FFMPEG_BUNDLE` | 11 | AC-25.4 reject + Open Questions ❌ option only | confirmed-consistent |
| `BUNDLE_RESOLVER` | 12 | named set + AC-25.4 + Files Modified + task 5 | updated |
| `SECRET_SENTINELS` | 13 | named set + AC-24.6 | updated |
| `VITEST_MEU25` | 14 | named set + AC-25.3/25.8 + task 5/7 | updated |
| `HANDOFF_COUNT = 2` | 15 | 0 | updated (gone) |
| `named-sets.json` | 16 | owner references | updated |

Blast-radius census: **16** values swept, **0** stale bare `PACK_DIST dir` / `ExpectedCount 10` / missing-artifact PASS left, new owners confirmed at every intended site.

### Not started

No product code, tests, or MEU handoffs were written. Implementation remains unchecked.

---

## Round 2 — 2026-08-24

### Intent Anchor

Executing this plan is intended to deliver the Session 12 Windows distribution contract for MEU-24 and MEU-25. Whether the corrected plan would now deliver that objective is not re-scored in this round because the mandatory PR-6 correction-evidence precondition is not satisfied.

### Current Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| PR6-1 | Procedural gate (unrated) | **PR-6 — The blast-radius census is undispositioned at the required per-hit level.** The index and all 16 unfiltered receipts exist and appear untruncated, and receipts 01–16 contain 63 raw `file:line` hits. However, the Corrections Applied log gives only query/category-level summaries (for example, all `PACK_DIST` substring hits are collectively called `confirmed-consistent`) rather than assigning `updated` or `confirmed-consistent` to each raw `file:line` hit. `plan-critical-review.md` requires the correction log to disposition each `file:line`; aggregate counts or category summaries are not sufficient. Under the Round-2+ PR-6 pre-verdict rule, no corrected content may be re-reviewed this round. | `.agent/workflows/plan-critical-review.md:256`; this file `:155-177`; `C:/Temp/av-kit/census-p7-index.txt`; `C:/Temp/av-kit/census-p7-01.txt`–`census-p7-16.txt` | Append a per-hit disposition ledger covering all 63 raw hits, with receipt number, exact `file:line`, and `updated` or `confirmed-consistent`. Preserve the zero-hit receipt results, then resubmit for Round 3. | open |

### PR-6 Gate Evidence

| Check | Result | Evidence |
|-------|--------|----------|
| Census index exists | pass | `C:/Temp/av-kit/census-p7-index.txt` lists receipts 01–16 with `rg` result codes. |
| All raw receipts exist | pass | `census-p7-01.txt` through `census-p7-16.txt` are present. |
| Receipts untruncated | pass | Full static reads showed complete raw output with no truncation marker; zero-hit receipts contain only the RTK banner. |
| Every raw hit dispositioned | fail | 63 raw `file:line` hits exist, but the Corrections Applied table records dispositions only by query/category and does not map each hit to a disposition. |

### F1–F6 Recheck Status

Not reviewed in Round 2, as required by the PR-6 pre-verdict procedural gate. The Round 1 `fixed` labels remain corrector claims, not independent-review confirmations.

### Commands Executed

Static evidence only: full `Get-Content` reads of the rolling review, census index, and census receipts 01–16; `Test-Path`/file metadata inventory; and static hit counting over receipt lines beginning with the review-plan path. No project tests, Electron build, NSIS packaging, repository tools, plan scripts, product files, tests, plans, or other handoffs were run or modified.

### Open Questions / Assumptions

None. The missing evidence shape is defined directly by PR-6 and does not require a product decision.

### Verdict

`changes_required` — the Round-2+ PR-6 census gate is not satisfied because the correction log does not disposition every raw `file:line` hit. This is the workflow's procedural exception to the normal High/Critical blocking threshold; no severity is assigned and F1–F6 were not re-reviewed.

### Residual Risk

The substantive correction state is intentionally unknown for this round. A Round 3 independent review must first verify the completed per-hit ledger and then re-check F1–F6 against the current plan/task files.

---

## Corrections Applied — 2026-08-24 after Round 2 PR6-1

**Corrector:** coordinator. Frontmatter left as r2 `changes_required` until independent Round 3. This section resolves **only** PR6-1 (per-hit ledger). Plan/task content is unchanged from the first corrections pass.

Canonical unfiltered ledger: `C:/Temp/av-kit/census-p7-per-hit-ledger.txt` (63 raw hits + 4 zero-hit receipts).

### Per-hit disposition ledger (PR-6)

| Receipt | File:Line | Disposition |
|---------|-----------|-------------|
| R01 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:45` | confirmed-consistent (PACK_DIST substring of PACK_DIST_DIR/EXE) |
| R01 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:48` | confirmed-consistent (PACK_DIST substring of PACK_DIST_DIR/EXE) |
| R01 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:63` | confirmed-consistent (PACK_DIST substring of PACK_DIST_DIR/EXE) |
| R01 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:102` | confirmed-consistent (PACK_DIST substring of PACK_DIST_DIR/EXE) |
| R01 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:103` | confirmed-consistent (PACK_DIST substring of PACK_DIST_DIR/EXE) |
| R01 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:104` | confirmed-consistent (PACK_DIST substring of PACK_DIST_DIR/EXE) |
| R01 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:110` | confirmed-consistent (PACK_DIST substring of PACK_DIST_DIR/EXE) |
| R01 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:205` | confirmed-consistent (PACK_DIST substring of PACK_DIST_DIR/EXE) |
| R01 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:246` | confirmed-consistent (PACK_DIST substring of PACK_DIST_DIR/EXE) |
| R02 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:45` | updated |
| R02 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:48` | updated |
| R02 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:63` | updated |
| R02 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:103` | updated |
| R02 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:110` | updated |
| R02 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:205` | updated |
| R02 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:246` | updated |
| R03 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:45` | updated |
| R03 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:104` | updated |
| R03 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:110` | updated |
| R03 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:205` | updated |
| R03 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:246` | updated |
| R04 | — | updated (zero hits) |
| R05 | — | updated (zero hits) |
| R06 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:59` | updated |
| R06 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:131` | updated |
| R06 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:313` | updated |
| R06 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:44` | updated |
| R07 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:47` | updated |
| R07 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:62` | updated |
| R07 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:131` | updated |
| R08 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:51` | updated |
| R08 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:56` | updated |
| R08 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:65` | updated |
| R08 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:102` | updated |
| R08 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:137` | updated |
| R08 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:301` | updated |
| R08 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:304` | updated |
| R09 | — | updated (zero hits) |
| R10 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:49` | updated |
| R10 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:64` | updated |
| R10 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:76` | updated |
| R10 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:121` | updated |
| R10 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:254` | updated |
| R11 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:248` | confirmed-consistent (rejected env-bridge only) |
| R11 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:355` | confirmed-consistent (rejected env-bridge only) |
| R12 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:48` | updated |
| R12 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:63` | updated |
| R12 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:113` | updated |
| R12 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:153` | updated |
| R12 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:248` | updated |
| R12 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:274` | updated |
| R12 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:354` | updated |
| R13 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:100` | updated |
| R13 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:201` | updated |
| R14 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:48` | updated |
| R14 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:50` | updated |
| R14 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:63` | updated |
| R14 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:154` | updated |
| R14 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:156` | updated |
| R14 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:247` | updated |
| R14 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:252` | updated |
| R14 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:316` | updated |
| R15 | — | updated (zero hits) |
| R16 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:51` | updated |
| R16 | `docs/execution/plans/2026-08-24-p7-distribution/task.md:56` | updated |
| R16 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:102` | updated |
| R16 | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md:304` | updated |

Count check: 63 `file:line` rows + 4 zero-hit receipts. No raw hit is undispositioned.

---

## Round 3 — 2026-08-24

### Intent Anchor

Executing the current plan is intended to deliver the Session 12 Windows distribution contract for MEU-24 and MEU-25: a secret-free localhost-only PyInstaller onedir backend and an NSIS package whose resources-root backend, FFmpeg, and MCP payloads match the selected production call chains. The Round 3 evidence shows the PR-6 correction gate is complete and the six Round 1 correction surfaces now bind those deliverables to fail-closed validation.

### Current Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

No open findings.

### PR-6 Gate Evidence

| Check | Result | Evidence |
|-------|--------|----------|
| Census index and raw receipts | pass | `C:/Temp/av-kit/census-p7-index.txt` and unfiltered receipts `census-p7-01.txt` through `census-p7-16.txt` remain present; receipts 04, 05, 09, and 15 are the four zero-hit receipts. |
| Per-hit ledger completeness | pass | Exact static reconciliation found `raw_hits=63`, `ledger_hits=63`, `missing=0`, `extra=0`, `raw_duplicates=0`, and `ledger_duplicates=0`. |
| Per-hit disposition validity | pass | Every nonzero receipt hit is keyed by receipt plus exact `file:line` and uses `updated` or `confirmed-consistent`; `invalid_dispositions=0`. The four zero-hit receipts each have an explicit `updated (zero hits)` marker. |
| Round 2 PR6-1 | fixed | The correction log at this file `:228-306` and canonical ledger `C:/Temp/av-kit/census-p7-per-hit-ledger.txt` disposition all raw hits individually. |

### Independent F1–F6 Recheck

| Finding | Result | Current-file evidence |
|---------|--------|-----------------------|
| F1 — onedir source ownership | pass | `PACK_DIST_DIR` and `PACK_DIST_EXE` are distinct (`implementation-plan.md:103-104`; `named-sets.json:13-14`); `EXTRA_RESOURCES.from` is the directory and explicitly rejects an exe-only source (`implementation-plan.md:110`, `:246`; `task.md:48`). |
| F2 — NSIS build and missing-artifact failure | pass | Task row 6 runs `npm run build`, then electron-builder, then `assert-nsis-pack.ps1` (`task.md:49`). The oracle requires a nonempty build receipt and exits 1 when no installer exists (`assert-nsis-pack.ps1:14-29`). |
| F3 — reachable bundled FFmpeg bridge | pass | The selected resolver derives the frozen executable's sibling `ffmpeg/ffmpeg.exe`; the production chain is `cli.main` -> `build_services` -> `bundled_ffmpeg()` -> `FFmpegAdapter` (`implementation-plan.md:113-115`, `:248`). `AVKIT_FFMPEG_BUNDLE` appears only as an explicitly rejected alternative (`implementation-plan.md:248`, `:355`). |
| F4 — secret-value oracle | pass | `SECRET_SENTINELS` requires two unique values to be absent from both returned serialization and exact file bytes, and AC-24.6 mutates an allowed field with a sentinel for the negative case (`implementation-plan.md:100`, `:201`). |
| F5 — native Vitest coverage | pass | AC-25.3 and AC-25.8 are both assigned to `VITEST_MEU25` (`implementation-plan.md:247`, `:252`); task rows 5 and 7 execute both named Vitest files (`task.md:48`, `:50`), which are also listed in `named-sets.json:18-21`. |
| F6 — executable single ownership | pass | `named-sets.json` owns red counts, `HANDOFF_COUNT`, `HANDOFFS`, `HUB_NEXT_AFTER`, and the pack paths (`named-sets.json:2-17`). `assert-red-oracle.ps1:14-24` loads red counts/prefixes; `assert-handoff-markers.ps1:3-20` loads handoff count/names/filter; hub checks load `HUB_NEXT_AFTER` from JSON (`task.md:51`, `:56`). Human-readable plan labels do not create an alternate executable owner. |

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| PR-1 Plan/task alignment | pass | The current plan and task retain MEU-24 -> MEU-25 -> NSIS pack -> closeout ordering, with the six corrected controls scheduled in matching task rows. |
| PR-2 Not-started confirmation | pass | Every implementation and closeout status in the current `task.md` remains `[ ]`; this is still a plan review. |
| PR-3 Task contract completeness | pass | Actionable task rows retain owner, deliverable, exact validation, dependencies/context, durable outputs, and status. |
| PR-4 Validation realism | pass | The NSIS build is attempted before the fail-closed artifact check, and the two production-language ACs are scheduled through focused Vitest commands. |
| PR-5 Source-backed planning | pass | The selected onedir, resources-root, frozen-sibling, descriptor, and MCP contracts retain explicit Spec, Local Canon, Research-backed, or prior-finding sources. |
| PR-6 Handoff/corrections readiness | pass | The 63-hit raw census and per-hit correction ledger reconcile exactly; both MEU handoffs remain explicit. |
| PR-7 Scope discipline | pass | The current Out of Scope table remains evidence-backed and does not disguise MEU-24/25 distribution work. |
| PR-8 Control reachability/totality | pass | F1-F5 now identify concrete observables, production chains, and adversarial negative cases; missing NSIS artifacts and sibling-resolution failures fail closed. |
| PR-9 Single-statement discipline | pass | Executable counts, handoff names, hub-next value, pack paths, and size cap are loaded from `named-sets.json` by their consumers. |

### Commands Executed

Static reads and read-only evidence analysis only:

- Full line-numbered reads of the current `implementation-plan.md`, `task.md`, `named-sets.json`, and the three assertion scripts.
- Full reads of the rolling review, census index, receipts 01-16, and the canonical per-hit ledger.
- Exact read-only receipt-to-ledger reconciliation recorded at `C:/Temp/av-kit/review-r3-pr6-reconciliation.txt`.
- Static ownership/control censuses recorded at `C:/Temp/av-kit/r3-f6-owner-census.txt` and `C:/Temp/av-kit/r3-f1-f5-census.txt`.
- Canonical-target pre-edit guard recorded at `C:/Temp/av-kit/review-r3-pre-edit-guard.txt`.

No project tests, repository tools, plan scripts, Electron builds, or packaging commands were run. No product, plan, test, or other handoff file was modified.

### Open Questions / Assumptions

None. The current plan selects each previously ambiguous behavior and no product decision remains for F1-F6.

### Required Follow-up

No `/plan-corrections` follow-up is required. This workflow stops after recording the Round 3 verdict; execution is outside this review request.

### Verdict

`approved` — PR-6 is complete at the required per-hit level, and independent current-file review confirms F1-F6 are materially resolved. There are zero open findings.

### Residual Risk

This is plan approval, not runtime distribution evidence. The planned PyInstaller smoke, NSIS build, bundled-FFmpeg behavior, and clean-Windows install/launch still require execution receipts under the task contract; no project tests or packaging commands were run during this static review.
