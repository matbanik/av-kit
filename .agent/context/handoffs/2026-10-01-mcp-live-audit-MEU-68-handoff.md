---
date: "2026-10-01"
project: "mcp-live-audit"
meu: "MEU-68"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md"
build_plan_section: "bp05s5.x"
agent: "claude-code-web (Claude Opus 5.5)"
reviewer: "claude-fable-5-1-subagent (user-authorized, human-review-decision.md)"
predecessor: "2026-09-30-tts-repair-MEU-62-handoff.md"
---

# Handoff: 2026-10-01-mcp-live-audit-MEU-68-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-68 — `mcp-live-audit`. A runner (`mcp-server/scripts/audit/`) that drives the **built** MCP server as an IDE client does: the SDK `Client` over stdio against `mcp-server/dist/index.js`, against an isolated spawned `python -m avkit_api` (H-2). It executes all 68 compound-tool actions, checks each one through a REST or filesystem observable, proves every destructive action refuses without `confirm`, cleans up, writes a report and a `mcp-audit-summary.v1` summary, and compares against a committed baseline. The workflow `/mcp-audit` and the skill `mcp-tool-audit` document it. The authoritative baseline was recorded on Windows (WINDOWS_GATE attempt 3, `65bfa42`, after the review corrections; attempts 1 at `8345599` and 2 at `a044446` are superseded).
**Build Plan Section**: `docs/build-plan/05-mcp-server.md` §MCP live audit (Phase 5)
**Predecessor**: [2026-09-30-tts-repair-MEU-62-handoff.md](2026-09-30-tts-repair-MEU-62-handoff.md) (H-3: the baseline waited for MEU-62; `SEQUENCING_GATE` at row 9)

**For the reviewer.** Test expectations that changed after Red, each source-backed and listed in the plan's §Execution amendments:
- A7 / D-15: the registry-tied counts moved 67 → 68 (`coverage.test.ts`, the fake-backend discovery count) when the merge brought `avkit_models.download_asset`.
- D-17: the `docs.test.ts` frontmatter regex accepts `\r?\n` (CRLF checkout on Windows).
- A3: the AC-68.1 negative oracle's mechanism (`token_missing` surfaces on the first tool call, exit 3), fixed before Red.
- A8 / D-14: `tts.cancel` runs the refusal oracle on a finished job and fails as a filed step failure.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-68.1 | integration | Launch as an IDE does: `MCP_LAUNCH`, `initialize`, only the launch-config env keys (A5 wording), API found through `backend.json` | Spec §Client; Local Canon `ipc.ts`, `config.ts` | `tests/audit/run-cli.test.ts` (`buildLaunch` env set); `tests/audit/runner-fake-backend.test.ts` (real `dist/index.js` over stdio; `AVKIT_API_TOKEN` omitted → `token_missing`, `launch.initialized` true, exit 3, A3a); Windows summary `launch` | ✅ |
| AC-68.2 | unit | No in-process shortcut under `mcp-server/scripts/` | Spec §Client | `run-cli.test.ts` (scan of `forbidden-imports.txt` patterns + seeded negative); `validate-task.sh scope b` (`rg -f`) | ✅ |
| AC-68.3 | unit | Discovery classification NEW / REMOVED / GHOST; schema/meta disagreement is a discovery `fail` | Zorivest §Phase 1 | `tests/audit/classify.test.ts` (three outcome fixtures + mismatch fixture) | ✅ |
| AC-68.4 | integration | Discovery against the built server: 8 tools, `AUDIT_ACTION_SET` | Spec §Phase 1 | `runner-fake-backend.test.ts` (8 tools / 68 actions); `classify.test.ts` 9th-tool negative (A3b); Windows summary `discovery` | ✅ (8 filed `schema_not_advertised` findings → `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`, D-12) |
| AC-68.5 | unit | Coverage of every action by `AUDIT_PLAN`; baseline entries equal `AUDIT_ACTION_SET` | Spec (`meu-registry.md:66`) | `tests/audit/coverage.test.ts` (68 pairs; removed step detected; the committed baseline equals `AUDIT_ACTION_SET` and every non-pass carries an `issue`, review F3) | ✅ |
| AC-68.6 | integration | `OBSERVABLE_RULE`: every `pass` carries an observable; a hollow success is `fail`/`hollow` | G25; Spec §Phase 2 | `classify.test.ts`; `runner-fake-backend.test.ts` (201 add + 404 get → `hollow`, exit 1) | ✅ |
| AC-68.7 | integration | `REFUSAL_ORACLE` for all 7 `DESTRUCTIVE_SET` members | Spec §Destructive; D-4 | `classify.test.ts` (`refusal_mutated`, `refusal_missing`); `runner-fake-backend.test.ts` (DELETE during refusal → `fail`); Windows run: all 7 refusals held | ✅ |
| AC-68.8 | integration | Isolation (H-2): `ISOLATION_GUARD` before any mutation; exit 3 with zero mutations otherwise | Human-approved H-2 | `tests/audit/isolation.test.ts`; `runner-fake-backend.test.ts` (exit 3, 0 lifecycle mutations); Windows summary `isolation.ok` | ✅ |
| AC-68.9 | integration | `CLEANUP_PREDICATE` | Zorivest §Cleanup | `tests/audit/ledger.test.ts`; `runner-fake-backend.test.ts`; `tests/audit/backend-spawn.test.ts` (never-ready backend killed, D-19); Windows `cleanup {ok, residuals [], backend_exited, root_removed}` | ✅ |
| AC-68.10 | unit | `DELTA` classification and baseline schema; malformed baseline → exit 4 | Zorivest §Phase 4 | `tests/audit/baseline.test.ts` (6 deltas, 4 malformed baselines) | ✅ |
| AC-68.11 | unit | `BASELINE_UPDATE_RULE` | Spec §Phase 4; cloud-local §2 | `baseline.test.ts` (container / REGRESSION / non-win32 → exit 2, file SHA-256 unchanged); `run-cli.test.ts` (missing `--baseline` with `--update-baseline` → exit 4, no launch, review F2) | ✅ |
| AC-68.12 | unit | Fail-closed tolerance (signature **and** env proof; authoritative counts every non-pass; unknown flag exit 4 with no spawn) | cloud-local §4 | `classify.test.ts`; `run-cli.test.ts` | ✅ |
| AC-68.13 | unit | Report and summary (header, scorecard, lifecycle matrix, functional table, issues log, DELTA; container banner; schema) | Zorivest §Output Format | `tests/audit/report.test.ts`; `.agent/context/MCP/mcp-tool-audit-report.md` | ✅ |
| AC-68.14 | unit | No secrets on disk | Spec §must not; PROFILE E5 | `tests/audit/redact.test.ts`; container outputs grep 0 | ✅ |
| AC-68.15 | integration | Authoritative Windows run meets `AUTHORITATIVE_ACCEPTANCE`; first baseline + report | Spec §Where it runs; H-3; grouping D-4 | `validate-task.sh windows-gate-check` and `findings-check` over `windows-gate-result.json`, `mcp-audit-summary.json`, `baseline-snapshot.json` | ✅ |
| AC-68.16 | integration | Workflow and skill documents, indexed, citations real | Spec §Deliverables | `tests/audit/docs.test.ts` (7 tests, incl. the `npm run audit-x` negative) | ✅ |
| AC-68.17 | unit | Typecheck covers `scripts/**`; D6 `mcp-audit` row | Local Canon D6; M4 | `validate-task.sh typecheck-red-green` (probe TS2322 Red → Green) | ✅ |
| AC-68.18 | unit | Spec hub reconciled; no `STALE_SPEC_PATTERNS`; BUILD_PLAN Phase 5 at closeout | Local Canon; D3 | `validate-task.sh docs` (fixed-string `rg`, 0 hits; negative proven at planning: 3 hit lines); BUILD_PLAN row at H2-2 | ✅ (BUILD_PLAN Phase 5 "approved" lands at H2-2) |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| audit Vitest (96 → 81 failing at Red) | `PASS red: 81 failing assertions, 15 passing, VITEST_ACS all named`; kinds `{'AssertionError': 81}`, 0 suite-load errors | `PASS green: 96 passed` at Part A (audit) / 318 (full MCP suite); after the A11–A13 corrections 112 (audit) / 334 (full) | `mcp-server/tests/audit/*.test.ts` |
| AC-68.17 typecheck probe | `tsc --noEmit -p tsconfig.json` passes with a type error in `classify.ts` (empty receipt) | `npm run typecheck` fails `scripts/audit/classify.ts(311,14): error TS2322`; passes after revert | `mcp-server/tsconfig.scripts.json`, `package.json` |
| AC-68.18 stale spec | fixed-string `rg` over the pre-row-7 section: 3 hit lines | 0 hits | `docs/build-plan/05-mcp-server.md` §MCP live audit |

The 15 tests passing at Red were neutral stubs or unstubbed subjects (`ACTION_INDEX` row count, the forbidden-imports scan), each paired with a failing negative in the same `describe` (walkthrough §Red).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s28-red","command":"bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh red","cwd":"/home/user/av-kit","scope":"UNIT_TESTS + RUNNER_TESTS + DOC_TESTS (mcp-server/tests/audit)","phase":"red","exit_code":0,"result":"pass","tested_state":"b330dfb tests + stubs, no runner implementation","output":"PASS red: 81 failing assertions, 15 passing, VITEST_ACS all named; failure kinds {'AssertionError': 81}","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s28-typecheck-red-green","command":"bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh typecheck-red-green","cwd":"/home/user/av-kit","scope":"AC-68.17 tsconfig.scripts.json + D6 row","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Part A working tree (row 5)","output":"probe: scripts/audit/classify.ts(311,14): error TS2322 | PASS AC-68.17 typecheck Red -> Green; D6 row registered","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s28-docs","command":"bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh docs","cwd":"/home/user/av-kit","scope":"DOC_TESTS + STALE_SPEC_PATTERNS over 05 §MCP live audit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Part A working tree (row 7)","output":"PASS green: 7 passed | PASS docs","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s28-gate-a","command":"bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh gate-a","cwd":"/home/user/av-kit","scope":"mcp-types, mcp-build, full MCP Vitest, scope a, AC-68.2, task lint","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Part A tree before the row-9 merge","output":"mcp-types exit 0 | mcp-build exit 0 | PASS green: 311 passed | PASS mcp-tests 311 > floor 215 | PASS scope a: 51 changed paths, all allowed | PASS AC-68.2","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s28-seqgate","command":"bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh seqgate","cwd":"/home/user/av-kit","scope":"SEQUENCING_GATE after merge 76465a0 of origin/main 0e18fbd","phase":"static","exit_code":0,"result":"pass","tested_state":"76465a0 + A7","output":"MEU-62 status approved | meu_status render --check pass | issue_triage render --check pass | PASS scope b: 51 changed paths, all allowed | PASS AC-68.2 | PASS SEQUENCING_GATE","fresh":true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s28-pregate-final", "command": "bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh pregate", "cwd": "/home/user/av-kit", "scope": "npm ci, uv sync --frozen --all-packages, mcp-types, mcp-build, mcp-tests, audit --mode container against a real spawned backend", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "efeee3e clean tree (A11-A13)", "output": "PASS green: 334 passed | mcp-audit container: 84/97 pass, 8 discovery finding(s), cleanup ok, exit 1 | PASS audit-container: 84 pass, 13 tolerated (download.cancel, transcript.compile, capture.capture skip_env with member/signature/proof all true; 9 blocked beneath download.cancel); filed step failures [tts.cancel confirmed_no_effect] | PASS pregate (non-authoritative)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s28-windows-gate-run", "command": null, "procedure": "validate-task.ps1 -Check windows-gate -QuietMachineConfirmed on P:/av-kit at 65bfa42 (clean tree): preflight, npm ci, uv sync --frozen --all-packages, mcp typecheck, build, tests, then npm run audit -- --mode authoritative --no-baseline --update-baseline; five return files committed as d9e2497", "observer": "Mat (user), relayed 2026-10-01", "exit_code": null, "cwd": "P:/av-kit", "scope": "WINDOWS_GATE attempt 3 (row 11, reopened by A12/A13), authoritative audit", "phase": "full", "result": "pass", "tested_state": "65bfa42605a253a46eca92881777c6901da88c98", "output": "all stages exit 0 except mcp-audit exit 1 (findings recorded); mcp_tests 334 passed / 0 failed; audit 97 steps: 96 pass, 1 fail (avkit_tts.cancel confirmed_no_effect), 0 skip_env, 0 blocked; transcript.resume transcripts_done 1 last_item_status Done; transcript.compile 112681 B, 1 section(s); download.cancel c Cancelled, processor Idle; cleanup ok; 8 schema_not_advertised findings", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s28-windows-gate-check", "command": "bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh windows-gate-check", "cwd": "/home/user/av-kit", "scope": "windows-gate-result.json, mcp-audit-summary.json, baseline-snapshot.json; worst-of census; GATED_PATHS unchanged since 65bfa42", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "d9e2497", "output": "PASS windows gate @ 65bfa42605a253a46eca92881777c6901da88c98: mcp_tests {'passed': 334, 'failed': 0, 'total': 334}; audit 68 actions, non-pass ['avkit_tts.cancel']", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s28-h1-verify", "command": "bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh h1-verify", "cwd": "/home/user/av-kit", "scope": "windows-gate-check, findings-check, scope b, AC-68.2, mcp typecheck on the final tree", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "d9e2497 + row-12 annotation", "output": "PASS findings: 1 non-pass, all filed | PASS scope b: 63 changed paths, all allowed | PASS AC-68.2: no toolset import in mcp-server/scripts | typecheck exit 0 | PASS h1-verify", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s28-h1-ssot-api", "command": "bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh ssot-review && bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh api-scope", "cwd": "/home/user/av-kit", "scope": "MEU-68 ready_for_review render; packages/ untouched (G8)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "d9e2497 + row-12 annotation", "output": "PASS ssot-review (MEU-68 ready_for_review) | PASS api-scope: no packages/ change vs 0e18fbd; OpenAPI skip-with-basis (G8 not triggered)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s28-corrections-red-green", "command": "npx vitest run tests/audit/transcript-oracle.test.ts tests/audit/run-cli.test.ts tests/audit/backend-spawn.test.ts (Red before the A11 fixes, Green after)", "cwd": "/home/user/av-kit/mcp-server", "scope": "review round 1 F1, F2, sibling S1", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "3c949fc", "output": "Red: 7 AssertionError (resume/compile/census) + missing step transcript.requeue.conflict + F2 spy called once + missing symbol startBackendProcess | Green: transcript-oracle 11/11, run-cli 11/11, backend-spawn 1/1", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s28-final-suite", "command": "npm --prefix mcp-server run build && npm --prefix mcp-server test", "cwd": "/home/user/av-kit", "scope": "full MCP Vitest incl. tests/audit (112) and the committed-baseline test (F3, R2-1)", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "d9e2497 + row-12 annotation", "output": "Test Files 22 passed (22) | Tests 334 passed (334)", "fresh": true}
```

### Authoritative run (Windows attempt 3, `65bfa42`)

Durable copies: [`mcp-audit-summary.json`](../../../docs/execution/plans/2026-10-01-mcp-live-audit/mcp-audit-summary.json), [`windows-gate-result.json`](../../../docs/execution/plans/2026-10-01-mcp-live-audit/windows-gate-result.json), [baseline](../../skills/mcp-tool-audit/resources/baseline-snapshot.json), [report](../MCP/mcp-tool-audit-report.md).

- 97 steps over 68 actions: 96 pass, 1 fail, 0 skip_env, 0 blocked. Attempt 1 (`8345599`, 95/96) is superseded: review F1 showed its transcript domain passed with nothing fetched. Attempts 2 and 3 fetched one transcript (`transcripts_done 1`) and compiled a 112,681 B volume with 1 section.
- First live passes of the Windows-only surfaces: `download.cancel`, `download.pause`, `download.get.done` (629,172 B), `capture.capture` (fullscreen PNG), `tts.generate` (MP3, 2.6 s), both `download_asset` steps.
- The one failure: `avkit_tts.cancel` `confirmed_no_effect` → `MCP-TTS-GENERATE-SYNCHRONOUS` (D-14). Discovery: 8 `schema_not_advertised` → `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` (D-12). The baseline carries those two issue ids under `BASELINE_ANNOTATION_RULE` (row 12).

### Quality Gate Results

```
mcp typecheck (src + scripts): 0 errors
mcp build: exit 0
mcp Vitest: 334 passed, 0 failed (Windows attempt 3 and container); audit suite 112 passed
mcp-audit authoritative: 96/97 pass, 1 filed fail, cleanup ok
scope b: 63 changed paths, all allowed; packages/ untouched (OpenAPI skip-with-basis)
pyright / ruff: not applicable (no Python changed)
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `mcp-server/scripts/audit/{types,schema,classify,ledger,redact,report,fixtures,census,observer,plan,discovery,client,backend,run}.ts` | new | ~3,400 | runner: closed enums, mini JSON-schema validator, verdict/DELTA/tolerance classification, ledger + cleanup, redaction, report, `AUDIT_PLAN` (97 steps / 68 actions), REST observer, isolated backend spawn, CLI (exit 0/1/2/3/4) |
| `mcp-server/scripts/audit/{summary,baseline}.schema.json` | new | 176 | `mcp-audit-summary.v1`, baseline schema |
| `mcp-server/tests/audit/*` | new | ~1,640 | 112 tests (UNIT/RUNNER/DOC, incl. `transcript-oracle`, `backend-spawn`), `fake-backend.ts`, `forbidden-imports.txt` |
| `mcp-server/tsconfig.scripts.json`, `mcp-server/package.json` | new / modified | 9 / ±3 | scripts typecheck; `audit` script |
| `.agent/workflows/mcp-audit.md`, `.agent/skills/mcp-tool-audit/SKILL.md`, both READMEs | new / modified | 139 / +2 | workflow and skill (AC-68.16) |
| `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` | new | 399 | first authoritative baseline (Windows), annotated row 12 |
| `.agent/context/MCP/mcp-tool-audit-report.md` | new | 245 | authoritative report |
| `docs/build-plan/05-mcp-server.md` | modified | ±23 | §MCP live audit reconciled (D-5, H-2, D-8) |
| `.agent/docs/commands.md` | modified | +1 | D6 `mcp-audit` runtime row |
| `.agent/context/known-issues.{yaml,md}`, `meu-status.yaml`, `meu-registry.md`, grouping, `current-focus.md`, `BUILD_PLAN.md` | modified | — | 5 issues filed; MEU-68 ready_for_review; Session 28 in review |
| `docs/execution/plans/2026-10-01-mcp-live-audit/*` | new | — | plan, task, decisions, validate-task.{sh,ps1}, walkthrough, evidence JSON |

No file under `packages/`, `ui/` or `mcp-server/src/` changed.

```diff
@@ mcp-server/package.json scripts
-    "typecheck": "tsc --noEmit"
+    "typecheck": "tsc --noEmit && tsc -p tsconfig.scripts.json",
+    "audit": "tsx scripts/audit/run.ts"
```

```diff
@@ mcp-server/tests/audit/docs.test.ts (D-17)
-      expect(read(file)).toMatch(/^---\n[\s\S]*?description:[\s\S]*?\n---\n/);
+      // CRLF-tolerant: the Windows checkout normalizes .md to CRLF (.gitattributes text=auto).
+      expect(read(file)).toMatch(/^---\r?\n[\s\S]*?description:[\s\S]*?\r?\n---\r?\n/);
```

```diff
@@ docs/build-plan/05-mcp-server.md §MCP live audit
-`mcp-server/tests` stub HTTP with `vi.fn()`; `tools-parity` and `action-index` prove the surface matches the GUI action index; …
+`mcp-server/tests` stub HTTP with `vi.fn()` and call `handleTool` in-process. `tools-parity` and `action-index` compare the surface against the hand-written tables in `mcp-server/tests/fixtures.ts`. … Reconciled 2026-10-01 against `ACTION_INDEX` (D-5).
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Deferred Items

None within MEU-68. Product defects the audit found are filed known issues, outside this MEU per the plan's §Stop Conditions: `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` (high), `MCP-TTS-GENERATE-SYNCHRONOUS` (high), `API-UNHANDLED-ERROR-OPAQUE`, `MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES`, `MCP-PACKAGED-ENTRY-UNREACHABLE` (candidate; the optional packaged probe was not run, no installed build).

---

## Decision Log

```yaml
decision_log:
  - id: H-1
    stage: planning
    question: "Codex CLI is unavailable in the cloud container; who reviews the plan and the execution?"
    resolution: human
    class: governance-value
    chosen: "Fable 5.1 subagent (Recommended)"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-09-28-p11-capture-settings/human-review-decision.md:1-30 — same route, Session 26", "docs/execution/plans/2026-09-28-p11-transcript-tts — Session 25 same route"]
    research: { engine: none, sources: [] }
    reasoning: "Only vendor-distinct machine rung (Codex) is absent; PROFILE B4 human review costs a round trip per round. Same-vendor deviation disclosed in human-review-decision.md."
    human_message_reference: "USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Fable 5.1 subagent (Recommended)'"
  - id: H-2
    stage: planning
    question: "Which backend does the authoritative audit hit, given destructive clear/remove and settings.set?"
    resolution: human
    class: one-way-door
    chosen: "Isolated spawned backend (Recommended)"
    source_tag: Human-approved
    precedents: ["tests/integration/test_backend_spawn.py:29-64 — spawns avkit_api with a temp app-data", "PROFILE E1 — deleting user media/data is an irreversible action"]
    research: { engine: none, sources: [] }
    reasoning: "download.clear/convert.clear against the user's live app would wipe real queues; an isolated backend runs every action with real binaries and no user-data risk."
    human_message_reference: "USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Isolated spawned backend (Recommended)'"
  - id: H-3
    stage: planning
    question: "MEU-68 depends on unplanned MEU-62; wait, or build now and baseline later?"
    resolution: human
    class: product-preference
    chosen: "Build now, baseline later"
    source_tag: Human-approved
    precedents: ["grouping 2026-09-30 D-4 — audit after TTS repair so the baseline records a working tts.generate", "Session 26 plan §Sequencing gate — gate before execution"]
    research: { engine: none, sources: [] }
    reasoning: "User chose parallelism over the recommended wait. D-4's intent is preserved: only the baseline waits for MEU-62 (SEQUENCING_GATE before Part B); PART_A_PATHS keeps Part A off Session 27's files."
    human_message_reference: "USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Build now, baseline later'"
  - id: D-1
    stage: planning
    question: "Runner language and location: mcp-server/scripts/audit.ts or tools/mcp_audit.py?"
    resolution: autonomous
    class: two-way
    chosen: "TypeScript under mcp-server/scripts/audit/, run with tsx, typechecked through tsconfig.scripts.json"
    source_tag: Local Canon
    precedents: ["docs/build-plan/05-mcp-server.md:295 — either location allowed", "mcp-server/package.json — @modelcontextprotocol/sdk ^1.30.0 and tsx already present", "mcp-server/tsconfig.json — rootDir src, so scripts/ needs its own config"]
    research: { engine: native, sources: ["https://github.com/modelcontextprotocol/typescript-sdk — Client + StdioClientTransport ship in the same SDK the server uses"] }
    reasoning: "TS reuses the server's SDK and zero new dependencies; Python would add the mcp package to uv.lock (a GATED_PATHS change Session 27 also touches). Two-way: the runner is dev tooling, not shipped."
  - id: D-2
    stage: planning
    question: "SDK client or MCP Inspector --cli?"
    resolution: autonomous
    class: two-way
    chosen: "SDK Client over stdio"
    source_tag: Research-backed
    precedents: ["docs/build-plan/05-mcp-server.md:296 — 'MCP Inspector --cli or the SDK client'"]
    research: { engine: native, sources: ["https://github.com/modelcontextprotocol/inspector/blob/main/clients/cli/README.md — one process per method; --tool-arg values are JSON-coerced", "https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/cli — CLI exposes tools/list and tools/call"] }
    reasoning: "One session for 67+ calls keeps server state and stderr in one place and allows typed per-step assertions; Inspector would spawn a server per call, coerce argument types, and add an npx dependency."
  - id: D-3
    stage: planning
    question: "How does the runner know the expected action set without importing toolsets?"
    resolution: autonomous
    class: two-way
    chosen: "Runner reads tools/list (inputSchema action literals + _meta.action_descriptions); a Vitest test (not the runner) proves AUDIT_PLAN and the baseline cover ACTION_INDEX"
    source_tag: Local Canon
    precedents: ["docs/build-plan/05-mcp-server.md:296 — never imports toolset modules", "mcp-server/src/toolsets/registry.ts:336-368 — _meta.action_descriptions registered per tool"]
    research: { engine: none, sources: [] }
    reasoning: "Keeps the runner a pure IDE-equivalent client while drift between code and audit plan still breaks npm test."
  - id: D-4
    stage: planning
    question: "What counts as a refusal for a destructive call without confirm?"
    resolution: autonomous
    class: two-way
    chosen: "isError:true AND observable unchanged; accept handler validation_error/confirm_required or SDK 'Input validation error' text"
    source_tag: Research-backed
    precedents: ["mcp-server/src/toolsets/registry.ts:261-272 — Zod rejects before confirmMissing", "mcp-server/tests/capture.test.ts:221-234 — expects validation_error, not confirm_required"]
    research: { engine: native, sources: ["https://github.com/modelcontextprotocol/typescript-sdk/issues/2879 — McpServer returns isError 'Input validation error: Invalid arguments for tool X' when inputSchema fails"] }
    reasoning: "Over a real client the SDK may reject before the handler, so the text varies by layer; the state check is the actual control and cannot be satisfied by any refusal that mutates."
  - id: D-5
    stage: planning
    question: "05 §MCP live audit names actions that do not exist (download status, settings reset/apply_defaults, health gpu/gpu_refresh); which governs?"
    resolution: autonomous
    class: two-way
    chosen: "ACTION_INDEX governs; correct the spec text (AC-68.18) and the GUI-action-index claim"
    source_tag: Local Canon
    precedents: ["mcp-server/src/toolsets/registry.ts:51-119 — the served surface", "mcp-server/tests/fixtures.ts — what action-index/tools-parity actually compare against"]
    research: { engine: none, sources: [] }
    reasoning: "The audit must exercise what the server serves; inventing actions would violate 05 §What this layer must not do."
  - id: D-6
    stage: planning
    question: "Fix the packaged-entrypoint/node_modules defect found during planning?"
    resolution: autonomous
    class: two-way
    chosen: "No; file MCP-PACKAGED-ENTRY-UNREACHABLE as a hypothesis known issue (row 1) and add an optional non-blocking packaged probe to the Windows request"
    source_tag: Local Canon
    precedents: ["mcp-server/src/index.ts:31-34 — guard", "docs/distribution/mcp.json.example — $RESOURCES/mcp-server/index.js", "ui/electron-builder.yml:32-33 — dist only", ".agent/docs/cloud-local-collaboration.md §7 — runtime root causes are hypotheses until the target confirms"]
    research: { engine: none, sources: [] }
    reasoning: "Packaging is Phase 7 scope and touches mcp-server/src and the installer; widening MEU-68 would break PART_A_PATHS isolation from Session 27. The probe turns the hypothesis into target evidence at no extra round trip."
  - id: D-7
    stage: planning
    question: "Which live YouTube fixtures?"
    resolution: autonomous
    class: two-way
    chosen: "AUDIT_FIXTURES: jNQXAC9IVRw (19 s) for the downloaded file, dQw4w9WgXcQ (backend SABR_PROBE_URL) as second queue item, @jawed one-video channel for transcripts; all overridable by flag"
    source_tag: Research-backed
    precedents: ["packages/infrastructure/src/avkit_infra/youtube/adapter.py:82 — SABR_PROBE_URL"]
    research: { engine: native, sources: ["https://en.wikipedia.org/wiki/Me_at_the_zoo — 19 s, first YouTube upload, on Jawed Karim's channel 'jawed'"] }
    reasoning: "Smallest stable public media keeps the run short and read-only (PROFILE E3); a one-video channel bounds the transcript job. Overrides cover a removed video without a code change."
  - id: D-8
    stage: planning
    question: "Spec says the container may run a 'mocked-backend subset'; what runs in the container?"
    resolution: autonomous
    class: two-way
    chosen: "Vitest fake-backend integration (mocked) AND a container run of the real runner against a real spawned backend, labelled non-authoritative, with ENV_BOUND_AUDIT; capture seeded via REST register mode"
    source_tag: Local Canon
    precedents: ["docs/build-plan/05-mcp-server.md:303 — Where it runs: container subset must say so", ".agent/docs/cloud-local-collaboration.md §4 — signature-proven census"]
    research: { engine: none, sources: [] }
    reasoning: "Strictly more evidence than a mocked-only subset and still never authoritative; the fake backend is what makes the negative oracles (hollow, refusal_mutated) deterministic."
  - id: D-9
    stage: planning
    question: "Where does the baseline live?"
    resolution: autonomous
    class: two-way
    chosen: ".agent/skills/mcp-tool-audit/resources/baseline-snapshot.json"
    source_tag: Local Canon
    precedents: ["_inspiration/_zorivest_mcp_tool_audit_skill.md §Related Files — resources/ relative to the skill"]
    research: { engine: none, sources: [] }
    reasoning: "05 names resources/baseline-snapshot.json without a root; the reference skill's layout resolves it."
  - id: D-10
    stage: planning
    question: "Compute the Zorivest consolidation score?"
    resolution: autonomous
    class: two-way
    chosen: "No; the report states consolidation n/a (8 compound tools, consolidation already done)"
    source_tag: Local Canon
    precedents: [".agent/context/known-issues.yaml:713-714"]
    research: { engine: none, sources: [] }
    reasoning: "The score's ideal (13) is a Zorivest target; av-kit has no consolidation backlog."
  - id: D-11
    stage: planning
    question: "rtk is absent in the container; how do container rows run?"
    resolution: autonomous
    class: two-way
    chosen: "Raw invocation (unfiltered equivalent of rtk proxy) in the container; rtk proxy on Windows"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-09-28-p11-capture-settings/task.md — 'Container runs: these invoke tools raw' (amendment A2)", ".agent/docs/cloud-local-collaboration.md §1 table — no rtk in the container"]
    research: { engine: none, sources: [] }
    reasoning: "Unfiltered output preserves exact evidence; the Windows gate keeps the RTK contract."
  - id: D-12
    stage: execution
    question: "The real server lists an empty inputSchema for every tool; how does the audit treat a product defect it finds in discovery?"
    resolution: autonomous
    class: two-way
    chosen: "Report it as a discovery finding (AC-68.3 unchanged), file MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA, read the action set from _meta.action_descriptions, and let the gate scripts tolerate only filed findings (FILED_FINDINGS, amendment A2)"
    source_tag: Local Canon
    precedents: ["implementation-plan.md §Stop Conditions — a product defect the runner finds goes to a known issue, not fixed here", "AUTHORITATIVE_ACCEPTANCE — every non-pass needs a filed issue", "MEU62_PENDING_TOLERANCE — script-side, issue-bound tolerance pattern"]
    research: { engine: none, sources: ["node_modules/@modelcontextprotocol/sdk/dist/esm/server/mcp.js:76-83 — EMPTY_OBJECT_JSON_SCHEMA for non-object input schemas"] }
    reasoning: "Fixing mcp-server/src breaks PART_A_PATHS and Session 27 isolation; silently passing discovery would hide the exact defect class the audit exists to catch. Two-way: when the issue is fixed the finding disappears and the baseline records FIXED."
  - id: D-13
    stage: execution
    question: "Which fixtures and step sequences make every lifecycle step's precondition deterministic against the real state machines?"
    resolution: autonomous
    class: two-way
    chosen: "4-video watch_videos playlist with a 3 s delay (two pause→stop cycles give Cancelled for requeue and retry; a 409 contract on Pending); three convert jobs (short, long, long), with a deferred pause that takes effect after the current job; a Big Buck Bunny download as the cancel target; REST-register capture seed (source scan)"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/transcript.py:412-423,546-589 — delay between items; pause/stop to Paused/Cancelled", "packages/core/src/avkit_core/domain/transcript.py:24-37 — TRANSCRIPT_PARENT_TRANSITIONS", "packages/core/src/avkit_core/services/download.py:255-282,398-420 — queue flags; apply_defaults_to_pending", "docs/build-plan/09-screenshot-capture.md:487,526 — capture remove deletes files"]
    research: { engine: none, sources: ["live probes on a scratch avkit_api, walkthrough §Row-3 pins"] }
    reasoning: "A one-video channel completes before a pause lands, so the Processing/Cancelled/Failed preconditions for requeue/retry are unreachable on a fast host (the R2-3 risk). The inter-item delay gives a deterministic pause window. Two-way: the fixture flags override every URL."
  - id: D-14
    stage: execution
    question: "TTS generate is synchronous, so a running job's id is never available to a client; how does the audit exercise avkit_tts.cancel?"
    resolution: autonomous
    class: two-way
    chosen: "Run the REFUSAL_ORACLE on the finished job; the confirmed cancel's no-effect is a failure carrying MCP-TTS-GENERATE-SYNCHRONOUS (FILED_STEP_FAILURES), not a skip or a weakened oracle"
    source_tag: Local Canon
    precedents: ["implementation-plan.md §Stop Conditions — product defects become known issues", "D-12 — filed discovery findings tolerated by issue id", "AUTHORITATIVE_ACCEPTANCE — a filed fail does not fail MEU-68"]
    research: { engine: none, sources: ["routes/tts.py:54-69; services/tts.py:110-200; mcp-server/src/client.ts:13-14; container audit 2026-10-01 job2 fetch_failed at 30005 ms"] }
    reasoning: "Cancelling a running job is unreachable through any client, so no honest pass is possible; a REST-side workaround would hide the defect the audit exists to surface."
  - id: H-4
    stage: planning
    question: "Execution authorization and gate location: where does the authoritative audit run, and is execution authorized?"
    resolution: human
    class: governance-value
    chosen: "A. Split like Sessions 25 and 26: container Part A plus one Windows WINDOWS_GATE triggered by Mat; commits, pushes and the row-9 origin/main merge on claude/sweet-goodall-mu69td authorized; no PR, merge to main, release or deploy"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-09-28-p11-capture-settings/human-gate-decision.md:1-40 — 'Split like Session 25 (Recommended)'", ".agent/docs/cloud-local-collaboration.md §2-§3 — authority is local"]
    research: { engine: none, sources: [] }
    reasoning: "The authoritative run needs Windows (capture, real downloads); the container builds and proves everything else. SIGN 1 and plan_to_exec_gate human make execution wait for the user."
    human_message_reference: "USER_EXPLICIT 2026-10-01 'proceed' (human-gate-decision.md §H-4)"
  - id: D-15
    stage: execution
    question: "The row-9 merge brought MEU-62's avkit_models.download_asset; do the registry-tied test counts change from 67 to 68?"
    resolution: autonomous
    class: two-way
    chosen: "Yes (amendment A7): AUDIT_ACTION_COUNT=68, two download_asset steps in AUDIT_PLAN, coverage.test.ts and the fake-backend discovery count move to 68; flagged for the execution reviewer"
    source_tag: Local Canon
    precedents: ["mcp-server/src/toolsets/registry.ts — download_asset appended after the capture rows (Session 27, 0e18fbd)", "AGENTS §Testing — a proven expectation change needs an amendment plus independent review"]
    research: { engine: none, sources: [] }
    reasoning: "The expectation tracks the served surface, which the approved dependency changed; keeping 67 would make the coverage test assert a stale registry. The change is source-backed and confined to the two count assertions."
  - id: D-16
    stage: execution
    question: "The watch_videos fixture breaks the backend adapter and the bot wall is per video; how are the transcript fixture and the network census proof made deterministic?"
    resolution: autonomous
    class: two-way
    chosen: "Amendment A9: a Blender Studio 9-video playlist replaces watch_videos; the ENV_BOUND_AUDIT network proof is per failing step URL (NETWORK_STEP_URLS); download.cancel joins the census with the bot-wall signature and a container-host proof"
    source_tag: Local Canon
    precedents: ["walkthrough.md §Container pregate attempts 2-3 — AttributeError on watch_videos; url_a extracts while url_c fails", ".agent/docs/cloud-local-collaboration.md §4 — signature-proven census, fail closed"]
    research: { engine: none, sources: ["YouTubeAdapter.extract_video_ids on three Blender Studio playlists in the container (3/9/4 ids)"] }
    reasoning: "A fixture that fails on every host is a test defect, not an env bound; a per-URL proof keeps tolerance exact where the coarse proof would either refuse a real bot wall or excuse a URL that extracted fine. Windows ran all of it live with zero skip_env."
  - id: D-17
    stage: execution
    question: "Three container-only assumptions would break the Windows gate (CRLF frontmatter, shell-quoted uv spawn, drive-letter case in isMain); fix before the request or let the gate find them?"
    resolution: autonomous
    class: two-way
    chosen: "Fix before the request: the docs.test.ts frontmatter regex accepts \\r?\\n, uv is spawned without a shell, and run.ts compares the entry path case-insensitively on win32"
    source_tag: Local Canon
    precedents: [".gitattributes text=auto — .md checks out as CRLF on Windows", "docs/execution/plans/2026-09-30-tts-repair handoff — each WINDOWS_GATE attempt costs a user round trip"]
    research: { engine: none, sources: [] }
    reasoning: "Each is a portability defect in test or runner code, not a behavior change; the CRLF regex change widens a line-ending match without changing what it asserts and is flagged for the reviewer. Fixing first made attempt 1 pass."
  - id: D-18
    stage: execution
    question: "transcript.compile produced a 37 B volume on Windows; was the transcript oracle sound?"
    resolution: autonomous
    class: two-way
    chosen: "No (review F1). Restore the plan's observable: transcript.resume polls until a transcript is fetched or an item Failed, transcript.compile requires transcripts_done >= 1 and a matching Contents count, and a container-only census member covers the IP-blocked caption fetch (amendment A11); WINDOWS_GATE attempt 2 re-records the baseline"
    source_tag: Local Canon
    precedents: ["implementation-plan.md AUDIT_PLAN transcript row — 'poll until >= 1 item is terminal'; observable 'an item terminal per REST'", "packages/core/src/avkit_core/services/transcript.py:415-420 — _pause is checked before item 0", "2026-10-01-mcp-live-audit-implementation-critical-review.md F1"]
    research: { engine: none, sources: ["container probe 2026-10-01: TranscriptAdapter raises TranscriptRetryableError (RequestBlocked) for the fixture's videos"] }
    reasoning: "The first reading (no captions on live VODs) was a hypothesis; the pause landed before item 0 on every cycle, so nothing was fetched and the audit certified an empty transcript, the G25 hollow case. Restoring the approved observable costs one Windows run; accepting it would leave the transcript domain unproven."
  - id: D-19
    stage: execution
    question: "A backend that never prints AVKIT_READY left its child process running, which held the runner open until an outer timeout; fix inside MEU-68?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: startBackendProcess stops the child (SIGTERM, then SIGKILL) before rethrowing and names its pid; spawnBackend delegates to it"
    source_tag: Local Canon
    precedents: ["implementation-plan.md CLEANUP_PREDICATE — backend_exited is part of cleanup", "walkthrough.md §Execution review round 1 — the 590 s hang"]
    research: { engine: none, sources: [] }
    reasoning: "The runner owns the processes it spawns; a hung authoritative run would cost a Windows round trip. The fix is local to the runner and covered by a cross-platform test (node as the never-ready child)."
  - id: D-22
    stage: execution
    question: "The container's YouTube wall also appears as HTTP 403 on the media fetch, outside the download.cancel census signature; how is it tolerated without weakening the census?"
    resolution: autonomous
    class: two-way
    chosen: "Amendment A13: the signature also matches 'HTTP Error 403: Forbidden', and the proof becomes the container host AND a direct yt-dlp test fetch of download_url_c failing with the same wall (mediaFetchBlocked)"
    source_tag: Local Canon
    precedents: [".agent/docs/cloud-local-collaboration.md §4 — signature-proven census, fail closed", "2026-10-01-mcp-live-audit-implementation-critical-review.md round 1 OOC-2 — host-only proof is weak"]
    research: { engine: none, sources: ["container probe 2026-10-01: yt-dlp download of aqz-KE-bpKQ and jNQXAC9IVRw -> HTTP Error 403: Forbidden; Windows attempts 1-3 downloaded both"] }
    reasoning: "The census refused the new form correctly; the fix accepts it only with a per-URL reproduction, which is stronger than the previous host-only proof. Authoritative mode tolerates nothing, and attempt 3 passed download.cancel live."
  - id: H-5
    stage: execution
    question: "F5: does avkit_tts.cancel's failure trigger the Stop Condition for MEU-62's surface (tts.*)?"
    resolution: human
    class: governance-value
    chosen: "Ratify D-14 (Recommended)"
    source_tag: Human-approved
    precedents: ["implementation-plan.md §Stop Conditions — fail in MEU-62's surface reopens MEU-62", "D-14 — tts.cancel is the synchronous POST /tts/generate route (MCP-TTS-GENERATE-SYNCHRONOUS)"]
    research: { engine: none, sources: [] }
    reasoning: "The failure is the pre-existing synchronous route, not MEU-62's asset work; the reviewer judged the classification defensible and asked for one-line human ratification."
    human_message_reference: "USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Ratify D-14 (Recommended)' (human-gate-decision.md §F5)"
  - id: H-6
    stage: execution
    question: "R2-1: fix the silent early return in coverage.test.ts now (WINDOWS_GATE attempt 3) or file it and fix later?"
    resolution: human
    class: product-preference
    chosen: "Fix now + attempt 3"
    source_tag: Human-approved
    precedents: ["AGENTS §Testing — no silent early returns in tests", "task.md H1-6 — a correction under GATED_PATHS reopens WINDOWS_GATE"]
    research: { engine: none, sources: [] }
    reasoning: "The user preferred a clean session over a deferred known issue; attempt 3 costs one short Windows run."
    human_message_reference: "USER_EXPLICIT 2026-10-01 AskUserQuestion answer 'Fix now + attempt 3' (human-gate-decision.md §R2-1)"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-01 | claude-code-web | Initial handoff after WINDOWS_GATE attempt 1 and H1-1..H1-4 |
| Submitted for review | 2026-10-01 | claude-code-web | Round 1 to claude-fable-5-1-subagent |
| Review complete | 2026-10-01 | claude-fable-5-1-subagent | Round 1: approved with 3 Medium / 2 Low (non-blocking) |
| Corrections applied | 2026-10-01 | claude-code-web | F1–F4 plus a sibling (A11); WINDOWS_GATE attempt 2 requested |
| Evidence refreshed | 2026-10-01 | claude-code-web | WINDOWS_GATE attempt 2 PASS (a044446 / 0434895); rows 12, H1-1..H1-5 re-run; round 2 requested |
| Review complete | 2026-10-01 | claude-fable-5-1-subagent | Round 2: approved; R2-1 open; F5 pending human |
| Corrections applied | 2026-10-01 | claude-code-web | R2-1 (A12), download.cancel proof (A13); F5 ratified by Mat; WINDOWS_GATE attempt 3 PASS (65bfa42 / d9e2497); round 3 requested |
| Review complete | 2026-10-01 | claude-fable-5-1-subagent | Round 3: approved; R3-1 (Low) filed as MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT |
