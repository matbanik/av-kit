---
date: "2026-11-04"
project: "release-rc1"
meu: "MEU-111"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md"
build_plan_section: "bp05"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-03-release-rc1-MEU-111-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-111, `mcp-image-fits-stdio`. `avkit_capture image` never sends an image the SDK's stdio reader can't take. Mat added this MEU to RC1 (D-185).
**Build Plan Section**: [05 §Image size limit (residual)](../../../docs/build-plan/05-mcp-server.md#image-size-limit-residual).
**Predecessor**: none. The [MEU-108 handoff](2026-11-03-release-rc1-MEU-108-handoff.md), the [MEU-109 handoff](2026-11-03-release-rc1-MEU-109-handoff.md), the [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md) and the [MEU-112 handoff](2026-11-03-release-rc1-MEU-112-handoff.md) are the same plan's other MEUs.

Before this MEU, the MCP cap matched REST at 15 MiB, but the image travels as base64 in one JSON line and the SDK's stdio client closes the transport when a line outgrows its 10 MiB buffer. The server stayed up; the client lost every tool until it reconnected (`MCP-IMAGE-OVER-STDIO-LIMIT`).

- **`IMAGE_FITS_STDIO`.** `IMAGE_MAX_BYTES` is 7,800,000: 10,400,000 B of base64 and a wire line of 10,400,098 B against the SDK's 10,485,760 B, measured. Above the cap the `payload_too_large` message tells the agent to read `original_path` or `annotated_path` from `avkit_capture get`.
- **The audit.** `capture.image` and `capture.image.annotated` accept that refusal only when REST's own image is larger than the cap. A refused smaller image, or a lost connection, fails the step. `simpleStep`'s `expectError` may now be a function of the result, so only the server's own refusal counts.
- **`AUDIT_IMAGE_CAP`.** The audit holds its own copy of the cap, pinned by a test, because AC-68.2 forbids importing the server (D-189).
- REST stays at 15 MiB, so OpenAPI and `tools/list` don't change. An oversize shot can no longer be seen through MCP as an image; the agent gets a path. MCP clients other than the SDK's weren't tested.
- **Fix generalization.** Checked 1 location in `mcp-server/src/toolsets/registry.ts` (the only place the server sends image content, `:351`). Fixed 1 instance. Skipped 0. Verified 0 remaining unaddressed instances. `routes/captures.py:48` and `tests/e2e/test_api_captures.py:42` still say 15 MiB because REST didn't change.

**The live audit.** Gate `mcp-audit` ran both image steps against the real backend: `capture.image` `MCP image 3490701 B == REST 3490701 B: true; PNG true`; `capture.image.annotated` `annotated MCP 3490733 B == REST: true`. That shot is well under the cap, so the live run proves the ordinary path and not the refusal. The refusal is proved by AC-111.2 through the real SDK client on the built server and by AC-111.4's unit tests.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md) §MEU-111. **Execution authorization:** `USER_EXPLICIT`, 2026-11-03, "create MIT license file / prepare whatever we need to build and publish the release rc1 candidate", and 2026-11-04, "approve tripple of the token budget and add MEU-111". Plan review approved at round 3. Mat's 2026-11-04 rulings (ECN-6) don't change this MEU's code, so only the gate record moved.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-111.1 | integration | An image of exactly 7,800,000 B returns intact through the real SDK stdio client from the built server, and the connection still answers a later call. | Spec (05 §Image size limit) | `mcp-server/tests/image-over-stdio.test.ts:98` | ✅ |
| AC-111.2 | integration | One byte over the cap, and 8,059,548 B (the real shot), each return a `payload_too_large` tool error naming `original_path`, and the connection still answers a later call. | Spec; Local Canon `MCP-IMAGE-OVER-STDIO-LIMIT` | `image-over-stdio.test.ts:107` | ✅ |
| AC-111.3 | unit | The cap's base64 length plus an envelope reserve fits the SDK's exported `STDIO_DEFAULT_MAX_BUFFER_SIZE` (imported from `@modelcontextprotocol/sdk/shared/stdio.js`), so an SDK change that lowers it fails this test. | Spec | `image-over-stdio.test.ts:121` | ✅ |
| AC-111.4 | unit | The audit's `capture.image` and `capture.image.annotated` steps pass on that refusal only when the REST image is larger than the cap; a refused smaller image or a lost connection fails the step. | Spec; 05 §MCP live audit | `mcp-server/tests/audit/capture-image-step.test.ts:53-76`; live steps pass in gate `mcp-audit` | ✅ |
| AC-68 (cross-ref) | regression | AC-68.2: the audit runner imports nothing from the server's tree. H1-2 attempt 1 failed it on this MEU's row 5b; corrected here (D-189, ECN-3). The forbidden-pattern list and test are unchanged. | plan ECN-3 | `mcp-server/tests/audit/run-cli.test.ts` (gate `mcp-tests`) | ✅ |
| AC-108 (cross-ref) | — | Owned by the MEU-108 handoff (the READY guard in the output handler) | plan §MEU-108 | [MEU-108 handoff](2026-11-03-release-rc1-MEU-108-handoff.md) | see MEU-108 |
| AC-109 (cross-ref) | — | Owned by the MEU-109 handoff (the output folder before FFmpeg starts) | plan §MEU-109 | [MEU-109 handoff](2026-11-03-release-rc1-MEU-109-handoff.md) | see MEU-109 |
| AC-110 (cross-ref) | — | Owned by the MEU-110 handoff (licence, version, build, packaged checks and release materials) | plan §MEU-110 | [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md) | see MEU-110 |
| AC-112 (cross-ref) | — | Owned by the MEU-112 handoff (the encoder chosen for one job) | plan §MEU-112 | [MEU-112 handoff](2026-11-03-release-rc1-MEU-112-handoff.md) | see MEU-112 |
| AC-24 (cross-ref) | regression | AC-24.10: the packaged backend folder holds its exe and support tree. It passed at row 0, not failed as the plan predicted, because this tree holds the gitignored outputs; it fails only in a clean clone, and CI deselects it (plan ECN-2) | plan ECN-2 | `tests/unit/test_packaging_backend.py:212` (gate `py-tests`) | ✅ |
| AC-25 (cross-ref) | regression | AC-25.7: the MCP snippet names the app-data folder, with no token or API base, fixed in `0eb59ab` before this baseline. AC-25.10: the NSIS check script exists and fails closed; same clean-clone note as AC-24.10 | plan ECN-2 | `tests/unit/test_packaging_installer.py:64`, `:94` (gate `py-tests`) | ✅ |
| AC-71 (cross-ref) | regression | AC-71.10: Electron with `ELECTRON_RUN_AS_NODE` on the dev server entry answers `initialize` as av-kit, and the fuse pin holds in `electron-builder.yml`, which row 7 edited | plan §Verification 1 | `ui/tests/unit/mcp-spawn-electron.test.ts:76` (gate `ui-tests`) | ✅ |
| AC-72 (cross-ref) | regression | AC-72.7: `THIRD_PARTY_NOTICES.md` stays hand-curated with its LGPL appendix and FFmpeg source section; it gains one pointer line to the generated list, and its `## FFmpeg` section names the re-pinned build | plan §MEU-110 | `tests/unit/test_packaging_installer.py:207` (gate `py-tests`) | ✅ |
| AC-92 (cross-ref) | regression | AC-92.4: the MCP entry runs through the app's own exe with `ELECTRON_RUN_AS_NODE`. It is the Local Canon behind AC-110.13, which row 11 proved on the RC build | plan AC-110.13 | row 11 MCP probe, in the [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-38.11, once row 5a moved the test's local copy of the cap (`:70`) | `expected undefined to be true` | pass | `mcp-server/tests/capture.test.ts:259` |
| AC-111.2 at 7,800,001 B | `expected 'image' to be 'tool_error'` | pass | `image-over-stdio.test.ts:107` |
| AC-111.2 at 8,059,548 B | `expected 'threw' to be 'tool_error'`: the connection closed | pass | `image-over-stdio.test.ts:107` |
| AC-111.3 | `expected 15728640 to be 7800000` | pass | `image-over-stdio.test.ts:121` |
| AC-111.4 (two steps) | `expected 'fail' to be 'pass'` | pass | `capture-image-step.test.ts` |
| AC-111.4 cap pin (correction) | `expected undefined to be 7800000` | pass | `capture-image-step.test.ts:53` |
| AC-68.2 (correction) | `expected [ Array(1) ] to deeply equal []` | pass | `run-cli.test.ts` |

AC-111.1 isn't required Red: an image of exactly the cap returned intact before the change too. The last two rows are the ECN-3 correction's own Red and Green, after H1-2 attempt 1 found the defect.

Receipts: Red `C:/Temp/av-kit/s44-111-red.txt`; Green `C:/Temp/av-kit/s44-111-green.txt`, `C:/Temp/av-kit/rc1/rows/row5b-typecheck.txt`; correction Red `C:/Temp/av-kit/s44-111-red-cap.txt`; correction Green `C:/Temp/av-kit/s44-111-green-cap.txt`, `s44-111-green-cap-build.txt`, `s44-111-green-cap-types.txt`; the size measurement `C:/Temp/av-kit/rc1/image-limit.txt`; the failing gate step `C:/Temp/av-kit/rc1/attempt-1/s44-D6-mcp-tests.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s44-111-red", "command": "pwsh -NoProfile -File row-5a.ps1 (task.md row 5a Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-111 Red: image-over-stdio.test.ts on the real built server and SDK client, capture-image-step.test.ts, the moved local cap, red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 (baseline.sha) plus rows 1 to 5a", "output": "Tests 6 failed | 30 passed. expected undefined to be true; expected 'image' to be 'tool_error' at 7800001; expected 'threw' to be 'tool_error' at 8059548; expected 15728640 to be 7800000; expected 'fail' to be 'pass' on both audit steps. red-check: 1 receipt(s), 3 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-111-green", "command": "pwsh -NoProfile -File row-5b.ps1 (task.md row 5b Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-111 Green: the cap, the refusal message and the audit steps, on three test files, with build and typecheck", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 5b, before ECN-3", "output": "Test Files 3 passed (3), Tests 36 passed (36). Typecheck exit 0. Expectations unchanged from Red. This row ran only three files, which is how the AC-68.2 defect reached H1-2."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-111-red-cap", "command": "rtk proxy npm --prefix mcp-server run test -- tests/audit/capture-image-step.test.ts tests/audit/run-cli.test.ts *> C:/Temp/av-kit/s44-111-red-cap.txt", "cwd": "P:/av-kit", "scope": "ECN-3 correction Red: the pin test added while plan.ts still imported the server's cap", "phase": "red", "exit_code": 1, "result": "fail", "tested_state": "HEAD 24e2735 plus rows 1 to 13 and the pin test", "output": "Tests 2 failed | 19 passed. expected undefined to be 7800000 (no AUDIT_IMAGE_CAP yet). expected [ Array(1) ] to deeply equal [] (AC-68.2's scan hit plan.ts)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-111-green-cap", "command": "rtk proxy npm --prefix mcp-server run build *> C:/Temp/av-kit/s44-111-green-cap-build.txt; rtk proxy npm --prefix mcp-server run typecheck *> C:/Temp/av-kit/s44-111-green-cap-types.txt; rtk proxy npm --prefix mcp-server run test *> C:/Temp/av-kit/s44-111-green-cap.txt", "cwd": "P:/av-kit", "scope": "ECN-3 correction Green: plan.ts holds AUDIT_IMAGE_CAP; the whole MCP suite, not three files", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 13 and the correction", "output": "Test Files 34 passed (34), Tests 466 passed (466). Build and typecheck exit 0. forbidden-imports.txt and the AC-68.2 test unchanged."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-gate-h1-2-attempt1", "command": "$env:TMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:TEMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-03-release-rc1/session-gate.ps1 *> C:/Temp/av-kit/s44-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s44-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE','build_inputs','mismatch','audit rule','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 attempt 1, the registered D6 gate, on the tree before the ECN-3 correction", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+ab9c5df667b9ca5ae9139129a9e0075c6b774bf96f173e13d8d9fae746342ea2", "output": "mcp-tests exit=1: 1 failed, 464 passed, tests/audit/run-cli.test.ts AC-68.2, the runner tree contains none of the forbidden imports, hit mcp-server/scripts/audit/plan.ts: src/toolsets. Every earlier step exit 0, including py-tests 1100 passed. ui-build through identity-after not_run (fail-fast).", "fresh": false}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-gate-h1-2", "command": "$env:TMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:TEMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-03-release-rc1/session-gate.ps1 *> C:/Temp/av-kit/s44-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s44-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE','build_inputs','mismatch','audit rule','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 attempt 6, the registered D6 gate, whole tree after ECN-6, ECN-7, ECN-8, ECN-9, ECN-10 and the rebuild", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "Every step exit 0 except mcp-audit exit 1, which audit-rule.py tolerated (rule exit 0). py-tests 1186 passed in 123.98s (0:02:03). ui-tests 108 files, 1138 passed. mcp-tests 34 files, 466 passed. ui-electron 182 passed (3.7m). mcp-audit authoritative: 98/99 pass, 0 discovery finding(s), cleanup ok, exit 1; the one failure is transcript.compile: no transcript fetched (transcripts_done 0, last_item_status Pending); live-rigging-snow_vol1.md 37 B. build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573, build record matches. task-contract 45 row(s). changed paths: 93 outside scope: [] head: 24e27354e35eccc0cfa7d7e76357e673a6e38c23 head moved (S4): False. baseline excused py [] ui []. tested_state before and after equal. session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK).", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus and the audit report were updated", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "Drift check passed — SSOT loaded (112 MEUs, 12 phases), rendered regions match on-disk content The copied audit report holds no gmail-form address."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-h1-4-openapi", "command": "rtk proxy uv run python -c '<task.md row H1-4 compare of baseline.sha and the working file>' *> C:/Temp/av-kit/openapi-check.txt", "cwd": "P:/av-kit", "scope": "H1-4: the committed OpenAPI file against baseline.sha", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "info.version: 0.1.0 -> 0.1.0rc1 components and paths unchanged: True The gate's openapi step exit 0."}
```

### Quality Gate Results

`s44-gate-h1-2` is the fresh full record, and it isn't a clean pass. Its last line is:

> session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK).

The gate exits 0 because D-186 tolerates exactly one state: `transcript.compile` is the only failure, it wrote a real output file, and a direct caption fetch from this machine is blocked right now. `audit-rule.py` checked all three (rule exit 0). The audit's own verdict stays non-pass (`mcp-audit authoritative: 98/99 pass, 0 discovery finding(s), cleanup ok, exit 1`), the audit report says so, and the baseline wasn't refreshed. Transcript isn't verified end to end from this machine. That run doesn't check the content of compiled output either (plan F7).

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract` (45 row(s)), `scope-paths` (93 changed paths, none outside scope, head not moved), `build-identity-selftest`, `audit-rule-selftest`, `audit-clear-selftest`: all exit 0.
- **Suites:** `py-tests` 1186 passed in 123.98s (0:02:03); `ui-tests` 108 files, 1138 passed; `mcp-tests` 34 files, 466 passed. Baseline failures excused: none.
- **Builds and state:** `mcp-build`, `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`, `build-record` (`build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573`): all exit 0.
- **Runtime:** `ui-electron` 182 passed (3.7m); `mcp-audit-clear` exit 0; `mcp-audit` 98 of 99, 0 discovery findings, cleanup ok.
- **Identity:** `tested_state` `24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382`, the same before and after. Row H1-2 set `TMP` and `TEMP` under ECN-2 (D-190).
- **Attempts:** attempt 1 (`s44-gate-h1-2-attempt1`, state `…+ab9c5df6…`) failed `mcp-tests` on AC-68.2, a defect in row 5b, with 1 failed and 464 passed. Later steps didn't run. Its receipts are archived. Attempt 2 (state `…+7eba916b…`) passed on the build from before Mat's rulings (`py-tests` 1100 passed, `ui-tests` 1111 passed, `mcp-tests` 466 passed, `ui-electron` 181 passed), and ECN-6 superseded it. Attempt 3 (state `…+f52fc9d6…`) passed on the build from before round 2's findings (`py-tests` 1186 passed, `ui-tests` 1115 passed, `mcp-tests` 466 passed, `ui-electron` 181 passed), and ECN-8 superseded it. Neither has a record here, because `durable_evidence.py --require-full` accepts a passing full record only for the state under review. Attempt 4 failed `ui-electron` with 2 failed and 179 passed, AC-88.12's clipboard primer and AC-66.14's test timeout, while Mat dismissed the main-process error dialogs that ECN-9 fixes. Later steps didn't run. Its receipts are in `C:/Temp/av-kit/rc1/attempt-4/`. Attempt 5 (state `…+08022c05…`) passed on the build from before round 3's finding (`py-tests` 1186 passed, `ui-tests` 1129 passed, `mcp-tests` 466 passed, `ui-electron` 182 passed), and ECN-10 superseded it, so it has no record here for the same reason. Its receipts are in `C:/Temp/av-kit/rc1/attempt-5/`. Attempt 6 is this run, after the fix for round 3's finding and rows 10 to 13 again.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `mcp-server/src/toolsets/capture.ts` | modified | `IMAGE_MAX_BYTES = 7_800_000`, with the reason |
| `mcp-server/src/toolsets/registry.ts` | modified | The refusal names `original_path` and `annotated_path` |
| `mcp-server/scripts/audit/plan.ts` | modified | `AUDIT_IMAGE_CAP`, `isImageRefusal`, `refusedImageObservation`, function form of `expectError`, the two image steps |
| `mcp-server/tests/image-over-stdio.test.ts` | new | AC-111.1 to AC-111.3 |
| `mcp-server/tests/audit/capture-image-step.test.ts` | new | AC-111.4 and the cap pin |
| `mcp-server/tests/capture.test.ts` | modified | The local copy of the cap |
| `docs/build-plan/05-mcp-server.md`, `09-screenshot-capture.md` | modified | §Image size limit (residual); the Phase 5 exception |

```diff
-export const IMAGE_MAX_BYTES = 15_728_640;
+// Its base64 plus the JSON-RPC envelope must fit the SDK's 10 MiB stdio buffer; a longer line closes the connection.
+export const IMAGE_MAX_BYTES = 7_800_000;
```

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | None open at approval. Findings by round are in the rolling review. | — | — | — |

### Verdict

Codex approved with no findings open and `intent_achieved: yes`, at report round 4 and ledger round 2 of 6 (dispatch `s44-exec-r4b`). The reviewer's verdict and its stated limits are in `2026-11-03-release-rc1-implementation-critical-review.md`. This line only points there.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A downscaled preview for an oversize shot | out-of-scope | — | plan §MEU-111: "A downscaled preview can come later." Not registered |
| MCP clients other than the SDK's | out-of-scope | — | plan §MEU-111: "MCP clients other than the SDK's weren't tested." |

---

## Decision Log

```yaml
decision_log:
  - id: D-189
    stage: execution
    question: "H1-2 attempt 1 failed AC-68.2 because row 5b imported the server's image cap into the audit runner. How should the audit know the cap?"
    resolution: autonomous
    class: two-way
    chosen: "Restate it as AUDIT_IMAGE_CAP in plan.ts, add a test that fails if it parts from the server's IMAGE_MAX_BYTES, and leave the forbidden-import list alone."
    source_tag: Local Canon
    precedents: ["mcp-server/tests/audit/run-cli.test.ts:10-26 the runner tree may not contain src/toolsets", "mcp-server/tests/capture.test.ts:70 a test already keeps its own copy of the cap"]
    research: { engine: none, sources: [] }
    reasoning: "AC-68.2 exists so the audit observes the server from outside. An exception in the forbidden list, or a re-export that passes the text scan, would both defeat that. A literal copy can drift, so the pin test catches it, and a raised server cap no longer changes what the audit accepts."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Initial MEU-111 handoff after H1-2 |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Gate rebound to H1-2 attempt 3 after Mat's rulings (ECN-6); this MEU's code didn't change |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Gate rebound to H1-2 attempt 5 after round 2's findings and Mat's crash report (ECN-8, ECN-9); this MEU's code didn't change |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Gate rebound to H1-2 attempt 6 after round 3's finding (ECN-10); this MEU's code didn't change |
