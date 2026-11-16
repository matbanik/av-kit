---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-15-triage-tool-fixes/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ttf-plan-2026-11-15-triage-tool-fixes"
round: 2
---

# Critical Review: 2026-11-15-triage-tool-fixes

> **Review Mode**: `plan`
> **Verdict**: `approved`

## Intent Anchor

`tools/issue_triage.py` writes UTF-8 to a redirected receipt and never crashes on a Windows console code page; `verify --deep` reports only a missing file that a path-shaped `resolution_path` names and never writes the register; and `discover` reports no candidate from a vendored or bundled tree, a binary file or its own source.

Intent achieved: yes, as an implementation plan. F1 and F2 are fixed in the specified behavior, acceptance cases and task rows. No new evidence-backed High or Critical defect was found. This approves execution of the plan; it does not certify unimplemented code.

## Scope

Rechecked the complete working-tree plan and task, all six existing plan-local helpers, Session 79 and both issue records, current CLI/verify/discover/triage code, the relevant tooling-test callers and adoption fixture, five doc surfaces, D6, HDP sections 4a/5/5a/6 and the expert-pass receipts. Applied PR-1 through PR-9 and the Materiality Gate, including the rule against escalating nearby variants after a correction. Claude Code/Anthropic authored the plan; Codex/OpenAI performed this independent review.

All writes were under `C:/Temp/av-kit`. No repository file was edited. No pytest, Vitest, npm, uv sync/lock, product build or network request ran. Product test and implementation-handoff paths remain absent and implementation rows remain unchecked. `session-gate.ps1` is scheduled for H1-2; its absence is expected.

| Reviewed file | SHA-256 |
|---|---|
| implementation-plan.md | c9aaaf3635fd555adf669fcfc218d5df2094689928420512718cefc9c5dd98d6 |
| task.md | 91380be1bfcbe120c460c92136e9dec96f2d485bef2de7181bd6ee52b1b2733a |
| live-smoke.py | a5da46f0df97d398d3bad2d16ac52bc2973ad06c0962f7e4949be9a969db5c3d |

The initial Findings table below is retained verbatim from round 1. Its historical `open` cells are superseded by the round-2 Prior Pass Summary.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | **DISCOVER_ROOTS omits existing generated/vendor trees and loses its exclusions for subroot scans.** High confidence. With the proposed set installed in memory, a repository-shaped fixture reports markers from `ui/out/main/index.js`, `ui/out-e2e/main/index.js` and `packaging/deno-win64/LICENSE.md`, alongside the intended own-source control. These are actual tree locations, identified as generated/fetched outputs in `.gitignore`; the live walker reaches their files. `--root mcp-server` also reports `bundle/index.mjs`, because its relative name no longer matches `mcp-server/bundle`. The unchanged live-smoke `noise_class` returns `None` for all three omitted root examples and would print them as `real:` instead of failing. Thus every currently specified AC can pass while a build/vendor marker still becomes a candidate during triage. Violates AC-13's no-noise smoke promise and the registered discover goal. | docs/execution/plans/2026-11-15-triage-tool-fixes/implementation-plan.md:126; tools/issue_triage/discover.py:248; docs/execution/plans/2026-11-15-triage-tool-fixes/live-smoke.py:69 | Inventory this repo's generated/fetched trees, including `ui/out`, `ui/out-e2e` and vendored packaging trees, without excluding owned `ui/src`, `mcp-server/src`, packaging specs/scripts or design notes. Make exclusion identity survive supported `--root` values, including roots inside an excluded tree. Extend AC-7/AC-10/AC-13 and the smoke oracle with omitted-tree and subroot negative cases. | open |
| F2 | High | yes | behavior | **PATH_CHECK treats a line annotation as part of the filename.** High confidence. The exact proposed PATH_LIKE predicate accepts `tools/issue_triage.py:199`, but the specified `root / value.strip()` existence check reports it missing although `tools/issue_triage.py` exists. The probe confirms ordinary relative paths, backslash paths and an absolute Windows path resolve correctly; the annotated existing reference alone becomes a false `file_missing`. A triaging agent recording a file:line reference therefore gets the same class of false warning this fix promises to remove. AC-4 tests only bare existing filenames, and AC-13 checks only path shape, so neither catches it. Violates AC-4's existing-file negative case and the registered only-missing-files goal. | docs/execution/plans/2026-11-15-triage-tool-fixes/implementation-plan.md:123 | Define handling for trailing numeric line/column annotations before filesystem lookup, preserving Windows drive colons. Add existing and missing annotated-file cases to AC-3/AC-4 and pin the normalized evidence path; alternatively reject annotations as non-file values, explicitly and without a false missing-file finding. | open |

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |

### Confirmed Fixes

- **F1:** DISCOVER_ROOTS now names the measured generated/vendor outputs; DISCOVER_ANCHOR uses repository identity and checks the scan root's ancestors before walking (`implementation-plan.md:127-128`, D-948 at `:394`, D-953 at `:451`). AC-7/AC-10/AC-13 (`:179`, `:182`, `:185`) and task rows 1/6 (`task.md:48`, `:55`) exercise the new behavior. The smoke's independent Git inventory, traversal checks and subroot scans are wired at `live-smoke.py:90`, `:214`, `:221` and `:236`. In-memory application of the specified changes preserved exactly five owned-source controls, skipped every original F1 example and nested native publish output, and returned nothing from excluded roots. A `.git` file worked as well as a directory.
- **F2:** PATH_LOCATION strips numeric line/column suffixes before lookup and evidence-path construction (`implementation-plan.md:123-124`, D-945 at `:349`); task row 4 names it (`task.md:52`). AC-3/AC-4 (`implementation-plan.md:175-176`) now cover both normalized missing references and existing annotated references. Probes resolved `tools/issue_triage.py:199`, a backslash equivalent and an absolute Windows path, while AC-4's five inputs produced exactly the two intended missing paths.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

None. The bounded residual notes below do not demonstrate a new failure of the registered goal and do not reopen F1 or F2.

## Q1 — Goal and acceptance coverage

Accepted the full mapping: UTF8_STREAMS → AC-1/2 and rows 1–2; PATH_LIKE/PATH_LOCATION/PATH_CHECK → AC-3/4 and rows 3–4; NO_COVERAGE_CHECK → AC-5; DEEP_READ_ONLY → AC-6; discovery rules → AC-7–10 and rows 5–6; ARCHIVE_DISMISSED → AC-11 and rows 7–8; DOC_LINES → AC-12 and row 9; live smoke → AC-13 and row 10; register closeout/render → AC-14 and row 11. No AC was added or dropped.

The changed rows now prove the two originally missing cases. No further delivery gap was demonstrated. Actual Green results remain execution work.

## Q2 — UTF8_STREAMS and the Red

Accepted the unchanged D-944 mechanism: reconfigure stdout/stderr before argparse, with AttributeError/ValueError/OSError suppressed. `main(argv)` has no supplied-stream parameter or promise to preserve an embedded caller's encoding. Capture objects without `reconfigure` survive the guard; binary child capture plus explicit UTF-8 decoding avoids locale-dependent test decoding.

Freshly reproduced the real Red on installed Windows Python: current `--help` under cp1252 exits 1 with UnicodeEncodeError. A TextIOWrapper probe of the proposed loop emitted UTF-8 arrow/warning bytes, replaced a lone surrogate and tolerated StringIO capture. File/pipe behavior is supported by that probe and the planned subprocess tests. An interactive console was not launched; no new claim of interactive runtime certification is made.

## Q3 — Deep verification and consumers

Accepted the F2 correction and both unchanged removals. PATH_LIKE rejects the specified prose, URLs and nonstrings; PATH_LOCATION normalizes accepted annotated file references, including drive-qualified paths. AC-4 fixes the normalized evidence path, preventing a successful lookup from being paired with the wrong filename. The regex also preserves the specified `:12` empty-result case and nonnumeric suffixes.

DEEP_READ_ONLY removes both CLI saves and the function's stamp/parameter; AC-6 covers data equality, unchanged register-copy bytes and both CLI exits. Plain `verify` retains its staleness reader, and the plan describes that consequence accurately. The tooling tests consume model, not the removed parameter or finding. D-946/D-947 retain only their disclosed M-6 conflicts under the supplied hand-over; no additional mandatory-human hit was demonstrated.

The four-field note matches `cloud-local-collaboration.md:316-317` and the expert pass: actual verification records last_checked/method/result/evidence_file together and renders. No remaining consumer was shown to require deep verification to stamp the date.

## Q4 — Discovery, anchoring and archive

Accepted the expanded exclusions for the actual F1 trees and owned-source controls. `fnmatchcase` receives normalized repository-relative paths; its `*` spans slashes, and probes confirmed nested `native/a/deep/publish` exclusion without hiding the source sibling. Both `.git` entry forms anchor repository/subroot scans correctly. Roots inside the specified excluded trees return no candidates.

Without any `.git` ancestor, the explicit fallback is the supplied scan root. This works for a whole exported-tree root; it does not discover a missing repository boundary when handed only an exported subdirectory. That is the stated fallback, and no new current-repository failure was demonstrated. No additional infrastructure is requested for it.

Nonblocking precision note on `implementation-plan.md:127`: “every directory pattern” overstates literal parity with `.gitignore`. `*.egg-info/` (`.gitignore:5`) is not represented, and `native/*/publish` does not cover the zero-intermediate-directory spelling `native/publish/` allowed by `native/**/publish/` (`.gitignore:30`). The original generated/vendor cases are fixed; these residual forms have no demonstrated new goal-level false finding. Do not treat the static table as a complete general gitignore implementation.

DISCOVER_BINARY remains the deliberately bounded first-8,000-byte NUL heuristic; its binary fixture and text control passed the in-memory probe. DISCOVER_SELF compares resolved module identity, preserving another file named discover.py. ARCHIVE_DISMISSED changes generated output placement, not register data; normal regeneration is deferred as explicitly scoped, with AC-11 retaining the other categories.

## Q5 — Docs, helper checks and gate

Accepted DOC_LINES and its byte-level check. Applied the actual TABLE to scratch copies of the five live docs: the check passed and four CRLF files plus the LF skill retained their endings. The fresh nine-case selftest passed, including the six intended refusal cases, box width and four-field note. Red-check's fresh selftest passed 36 fixtures (11 positive, 25 negative), with zero wrong outcomes.

The revised smoke now obtains 68 ignored directory entries from Git independently of INVENTORY, classifies every original F1 example, and leaves the owned-source controls unclassified as noise. A Git-only injected tree was recognized without adding it to INVENTORY; a failed Git command recorded a problem, preventing silent oracle loss. CLI counts, subroot identities, walker liveness, leaked-path detection and inside-excluded-root checks are wired. The smoke was inspected and its oracle extracted in isolation; the whole pre-Green smoke was not run. It is appropriately a live check of present trees, while AC-7/10 supply synthetic regression cases.

`issue-resolve.py` stages via model.save, restricts parsed changes to the named issues/fields, checks grammar and decision-log round trips, and holds a deny-writer Windows handle with the expected hash. `baseline.ps1` makes working-byte copies/hash maps; `identity.py` binds code/tests/config/runtime and the plan's scripts, while excluding administrative outputs. Neither write path nor the whole-tree identity reader was run by this reviewer. The scheduled session gate includes triage unit tests, both tooling register callers, adoption tests, full `tests/`, and both state/issue render checks (`implementation-plan.md:303-307`). No new materially false-passing gate was demonstrated.

## Q6 — Order, baselines and write safety

Accepted row 0 and S2/S4 under the stated execution order. The four tool files are exclusively this session's code scope and are compared to HEAD. Shared docs/registers are instead bound to working bytes at row 0, allowing Sessions 75–78 to remain uncommitted. The register updater checks the row-0 hash under its held handle; unrelated dirty paths are preserved. Other planners' new plan folders are an explicit concurrency exclusion. Session 83's later render dependency is consistent with this sequence.

The live smoke copies the real register, directs both CLI commands to that copy, uses discover `--dry-run` and checks copy bytes plus the real register hash. Reviewer probes left the real register SHA-256 unchanged at `fe3dac63fabb8a1515bc82a4398398e83f590b13495587ba55adc538a684b202`. Planned tracked edits remain within the declared inventory and closeout outputs; ordinary ignored environment/test-cache side effects belong to execution validation.

The supplied source request authorizes execution after approval and leaves this session uncommitted with a message draft. Its explicit authorization governs the draft's generic instruction to wait for another message. No commit or push is authorized by this verdict.

## Checklist Results

Manual observations: codex-independent-reviewer, null exit. Command probes used `PYTHONDONTWRITEBYTECODE=1`, UTF-8 reviewer output and receipts under `C:/Temp/av-kit`; helper temporary directories were also placed there.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare complete plan, task rows and changed ACs | null | Same goal, 14 ACs and dependency order; rows 1/4/6 carry new mechanisms |
| PR-2 Not started | pass | Read task and inspect test/handoff paths | null | Implementation unchecked; both paths absent |
| PR-3 Task contracts | pass | Inspect owners, deliverables, validations and statuses | null | Required execution steps represented |
| PR-4 Validation realism | pass | Trace changed ACs to rows and run isolated probes | null | Original F1/F2 examples now covered and correct |
| PR-5 Source-backed choices | pass | Read issues, grouping, HDP and expert receipts | null | Sound reversibility and delegated M-6 choices; no additional human-only decision found |
| PR-6 Corrections readiness | pass | Compare original findings to changed contracts, ACs and helper | null | Both findings have observable corrective behavior and regression cases; paperwork is outside the supplied review scope |
| PR-7 Scope discipline | pass | Compare boundaries to goal and Session 79 | null | No required goal clause removed; literal gitignore parity caveat recorded once |
| PR-8 Reachability / negative oracles | pass | Trace main → command → verifier/scanner; inspect smoke | null | Production call chain and negative cases reach actual observables |
| PR-9 Single-statement discipline | pass | Compare named definitions with AC/row references | null | No materially ambiguous competing behavior definition |
| Changed-contract / doc probes | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/ttf-r2-probes.py` | 0 | F1/F2 cases, `.git` forms, no-git fallback, oracle controls and actual doc edits passed |
| Encoding / readiness probes | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/ttf-r2-final-probes.py` | 0 | Current cp1252 help Red reproduced; proposed stream loop controls passed |
| Doc selftest | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-15-triage-tool-fixes/doc-check.py --selftest` | 0 | `doc-check selftest: 9/9 ok` |
| Red selftest | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-15-triage-tool-fixes/red-check.py --selftest` | 0 | `36 fixture(s) (11 positive, 25 negative), 0 wrong: []` |
| Report structure / target / round | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/ttf-plan-review-round-2.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-15-triage-tool-fixes/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/triage-tool-fixes/review/round-2-report-state.json` | 0 | `review_mode=plan; round 2 of 3; verdict=approved; open findings=0` |
| Product suites / whole live smoke / baseline | n/a | Not run in this read-only plan review | null | No implementation certification claimed |

```json
{"schema_version":"evidence.v1","check_id":"ttf-r2-changed-contracts","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/ttf-r2-probes.py","cwd":"P:/av-kit","scope":"Session 79 revised plan contracts; in-memory code and scratch fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-sha256:c9aaaf3635fd555adf669fcfc218d5df2094689928420512718cefc9c5dd98d6;task-sha256:91380be1bfcbe120c460c92136e9dec96f2d485bef2de7181bd6ee52b1b2733a;smoke-sha256:a5da46f0df97d398d3bad2d16ac52bc2973ad06c0962f7e4949be9a969db5c3d","output":"Directory and file .git fixtures preserve exactly five source controls; mcp-server subroot yields src/a.ts only; excluded roots yield none; nested native publish is excluded. No-.git whole-root fallback passes. Existing annotated relative/backslash/absolute Windows references resolve; AC-4 yields exactly missing/file.py and gone/other.py. Smoke oracle obtains 68 Git ignored trees, recognizes Git-only noise and records Git failure. Actual five-doc transformation passes with CRLF/LF kept. Real register hash unchanged. round-2 probes: pass.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"ttf-r2-doc-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-15-triage-tool-fixes/doc-check.py --selftest","cwd":"P:/av-kit","scope":"Plan-local documentation checker","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-sha256:c9aaaf3635fd555adf669fcfc218d5df2094689928420512718cefc9c5dd98d6","output":"doc-check selftest: 9/9 ok; expected refusal cases returned 1 or 2, positive/box/note controls passed.","fresh":true}
```

## Verdict

`approved` — round-1 F1 and F2 are fixed at the plan level. No new evidence-backed High or Critical finding blocks execution. Residual limits are the fixed-list parity wording, the explicit no-.git fallback, the bounded binary heuristic and unrun future implementation gates; none is presented as implementation evidence.

Complete rolling report: `C:/Temp/av-kit/ttf-plan-review-round-2.md`. The coordinator owns the byte-for-byte canonical copy and ledger recording. All repository files remain untouched by this review.
