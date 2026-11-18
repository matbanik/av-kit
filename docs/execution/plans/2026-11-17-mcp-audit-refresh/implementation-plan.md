---
project: "2026-11-17-mcp-audit-refresh"
date: "2026-11-17"
source: "grouping .agent/context/grouping/2026-11-17-value-triage-session-grouping.md §3 Session 92; issues MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT, MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL (D-1134 A) and MCP-AUDIT-BASELINE-PENDING-CROP (D-1132)"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
---

# Implementation Plan: sample the census network proofs, describe avkit_capture, and record the pending baseline actions

> **Project**: `2026-11-17-mcp-audit-refresh`
> **Build Plan Section(s)**: none. This is audit and tool-description debt with no MEU, as in Sessions 78, 79 and 90 and grouping D-1132; D-1155 records why the `avkit_capture` description change takes no MEU either.
> **Status**: said to execute (USER_EXPLICIT 2026-11-17 "orchestrate the plan creation for all sessions and proceed with execution for each"). `plan_to_exec_gate: human`: that message is the execution approval once the plan review approves; the plan review was approved at round 1 (.agent/context/handoffs/2026-11-17-mcp-audit-refresh-plan-critical-review.md). Mat ruled D-1159 A on 2026-11-18. Session 92 is third in the queue (D-1133: 74, 91, 92, 93, 94); Sessions 74 and 91 run and are committed before it.

---

## Goal

**Goal anchor:** in container mode the audit runner samples each census network proof up to three times, about 5 s apart, and a proof holds when any sample is blocked, so one lucky fetch no longer turns an environment failure into a counted one; `.agent/workflows/mcp-audit.md` says so in one note; `avkit_capture`'s top-level tool description is a real one, built from its existing per-action text with the sentences every action repeats removed and the two facts the Session 64 eval missed first (call `image` to view a frame or sheet; call `sheet` again over a narrower span to zoom), under 4,096 characters, while `_meta.action_descriptions`, every input schema and the other seven tool descriptions stay byte-identical (D-1134 A); the three Session 64 eval tasks pass on the new description; and one authoritative Windows audit run with clean cleanup and no regression records, as Mat ruled (D-1159 A), the five served actions that `BASELINE_PENDING` holds (`avkit_convert.probe`, `avkit_capture.crop`, `.frames`, `.sheet` and `.export`) into the committed baseline and report, with `BASELINE_PENDING` emptied in the same change; no file under `packages/`, `tools/`, `ui/` or `tests/` changes, and no API route or OpenAPI document changes. Tests and scripts prove each part; there is no manual check.

**Why.**

- **`MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT`** (`known-issues.yaml:1191`, MEU-68). The census proof for a network member is one direct fetch per URL (`mcp-server/scripts/audit/run.ts:547-577`). When the network blocks the audit's own call and then lets the proof's fetch through, the proof fails and a real environment failure is counted as a product failure. The resolution path: "Sample each census network probe up to 3 times (proof holds only if every sample fails with the signature) and add a re-run note to .agent/workflows/mcp-audit.md. Batch with the next change under the MCP audit GATED_PATHS." D-1156 records why this plan takes "any sample blocked" instead of the literal "every sample".
- **`MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`** (`:5126`, MEU-131). A model that loads the tools upfront sees each tool's top-level description and flattened input schema, not `_meta.action_descriptions`. `avkit_capture`'s top-level text is 145 characters (`registry.ts:172`), so in the Session 64 eval two of the three real-surface runs missed facts that only the action text held (`C:/Temp/av-kit/s64-E4-check.txt`: t1 made no `image` call; t2 made one `sheet` call where two were needed). Mat ruled D-1134 A on 2026-11-17 ("D-1134: A").
- **`MCP-AUDIT-BASELINE-PENDING-CROP`** (`:5021`, MEU-130, D-499). The committed baseline (`.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`, 70 entries, all `pass`) lacks the actions served since it was written; `coverage.test.ts:23-29` lists them in `BASELINE_PENDING`. The notes: "Closed by the next authoritative baseline update, which records avkit_capture.crop and empties BASELINE_PENDING in the same change; AC-130.28 fails once the baseline holds a pending key". The caption block that stopped a clean authoritative run has lifted (`YOUTUBE-CAPTIONS-IP-BLOCK` resolved, D-1125; the issue's 2026-11-17 triage note).

**Grouping §3 Session 92** (grouping `:99-109`): the order is the census proof, then the `avkit_capture` description (D-1134 A), then the baseline; "The audit reads only action keys, so the baseline does not change for it"; the gate rule is "`--update-baseline` only from an authoritative Windows run with clean cleanup and no regression (BASELINE_UPDATE_RULE). The baseline is an MCP contract record; any tool-shape change in it is Mat's (M-4). Mat has ruled the `avkit_capture` description (D-1134); any other description change goes back to Mat."; cloud/local is local; calibrate against the 2026-10-01 `mcp-live-audit` session and Session 59 `capture-crop-copy`. Grouping §5 (`:151`): "Session 92: captions still fetch from this network at its start." Mat 2026-11-16: "This should be done with framework and scripts!", so nothing here is a manual check.

**What the code shows (plan-time reads at `HEAD` `ecfa3f3`, `mar92-probe.txt`):**

- **The census proof.** `run.ts` (CRLF) holds three probes: `youtubeExtractWorks(url)` (`:353`), `mediaFetchBlocked(url, wall)` (`:368`) and `captionFetchBlocked(sourceUrl)` (`:389`). Each runs `spawnSync("uv", ["run", "python", "-c", code, url], { cwd: REPO_ROOT, encoding: "utf8", timeout: 180_000 })` once. The census block (`:547-577`) runs only when `options.mode === "container" && fixtures` (`:555`): for each `ENV_BOUND_AUDIT` member with a failing record that matches its signature, `:564` sets `probe[member.key] = !urls.every((url) => url !== undefined && !youtubeExtractWorks(url))`; cancel uses `mediaFetchBlocked(fixtures.download_url_c, cancel.signature)` and compile `captionFetchBlocked(fixtures.transcript_source_url)`; `:576` sets `env.networkProbe` when any key was probed. `census.ts` lets a proof hold when `env.networkProbe?.[key] === false`. `NETWORK_STEP_URLS` (`plan.ts:775`) maps `download.add.a/b/c` to `download_url_a/b/c` and `transcript.add` to `transcript_source_url`. `AuditDeps` (`:102-107`) is the runner's existing test seam (`launcher`, `steps`, `platform`, `mutateLaunch`); the probes have none, so no test reaches them today. The authoritative mode never gathers a proof.
- **The forbidden-import scan.** `tests/audit/run-cli.test.ts:91-103` (AC-68.2) scans every file under `mcp-server/scripts` for the strings in `tests/audit/forbidden-imports.txt` (`src/toolsets`, `dist/toolsets`, `handleTool`, `registerMcpSurface`), comments included, so the new script file must hold none of them (`FORBIDDEN_IMPORTS_KEPT`).
- **The descriptions.** `registry.ts` (CRLF) `TOOL_TOP_LEVEL` (`:164-173`) holds one short line per tool, used at `:624` (`description: TOOL_TOP_LEVEL[name]`). `capture.ts` (CRLF) builds the 14 per-action texts in `captureDescriptions` (`:94`) from `desc()` (`:33-40`, four shared marker sentences), `IMPORT_TEXT`, `REGION_VIEW_TEXT`, `CROP_TEXT`, the `FRAMES_TEXT` and `SHEET_TEXT` arrays (`:58`, `:71`; `:79` is "To zoom, call again with a narrower start and end; no state is kept between calls."), `EXPORT_TEXT` and `ANNOTATE_EXAMPLE` (`:91`); the flatten, revert and annotate-newline sentences are inline. The `_meta.action_descriptions` keys are bare action names (`mar-plan-desc-record.json`). No test pins a top-level description: `m7-resource.test.ts` and `capture.test.ts` read the per-action texts only (both stay byte-identical). The row-0 lengths and SHA-256 of all eight top-level descriptions are in `mar-plan-desc-record.json`; capture's is 145 characters.
- **The candidate description.** `capture-description.expected.txt` (this folder, LF, 3,989 bytes, 3,981 characters, 14 lines, no trailing newline). Line 1 is the lead; lines 2 to 5 carry the four markers once each; lines 6 to 14 hold one line per action in the `ACTION_INDEX` order of the actions that add their own text (image, capture, annotate, flatten, revert, crop, frames, sheet, export). `mar92-trace-probe.txt`: every sentence of lines 6 to 14 is a substring of that action's `_meta` text, and no other line starts with a marker.
- **The Session 64 eval.** `docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md` (Session 64, D-608): `eval-harness.ts <ROOT> describe` prints the surface a model sees; a fresh `general-purpose` subagent with `model: haiku` runs each task through `eval-harness.ts <ROOT> call …`, which starts the isolated real backend over its own root, with an allowlist and local media (execution note, Session 92: the reviewed plan said a fake backend; the harness starts the isolated real `spawnBackend`, eval-harness.ts:30,78-85,99-107; plan review non-blocking note); `eval-check.py check_run` judges each run against `C:/Temp/av-kit/s64/eval-key/answers.json`. `eval-rerun.py --session64` reproduces Session 64's real-surface result at plan time (`mar-plan-eval-session64.txt`: t1 and t2 fail, t3 passes).
- **The baseline and its tests.** `baseline-snapshot.json` (CRLF, 7,150 bytes) holds 70 entries, all `pass`, `findings: []`. `coverage.test.ts` (CRLF) `:15-22` says the next authoritative update "adds them, empties this list and closes MCP-AUDIT-BASELINE-PENDING-CROP", and MEU-133 to MEU-136 each added their key "on the same terms". AC-68.5 and AC-130.28 compare the baseline with `AUDIT_ACTION_SET` less `BASELINE_PENDING`; `:165` feeds `pendingProblems` a fixture; the AC-135.19 test (`:299-304`) and the AC-136.18 test (`:328-332`) assert that `BASELINE_PENDING` ends with the sheet and export keys. `writeBaselineIfAllowed` writes LF JSON with one entry per served action (`run.ts:590-610`), so the update turns the file from CRLF to LF through the tool; nobody converts it by hand. `recorded_commit` is `git rev-parse HEAD` with no dirty check (`run.ts` `gitCommit()`), so the record names the commit under this session's uncommitted change.
- **The audit's backend.** `backend.ts:108-155` starts its own backend in a `mkdtemp` root under `os.tmpdir()`, with fresh tokens and its own `app-data/mcp-token.txt`. The audit never reads `.mcp.json`, Mat's app data or Mat's token, and never talks to the avkit MCP server Mat's IDE runs.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-17). The change touches the audit runner's census block, one tool description and the baseline test, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go under `C:/Temp/av-kit/mcp-audit-refresh/`, named `mar-*` (planning receipts are `mar92-*` and `mar-plan-*`).
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE` (Session 88 RULE-3).
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\mcp-server'`, never from the Bash tool, and returns to `P:\av-kit`.
  - Every audit run and every Vitest run sets `TMP` and `TEMP` to `C:\Temp\av-kit\mcp-audit-refresh\tmp` (`AUDIT_TMP`).
  - No row starts the desktop app. The audit starts its own backend and its own MCP server child and stops them itself; its cleanup record is checked. No row stops a process by name.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local (the authoritative audit needs the Windows host; grouping §3 "Cloud/local: local").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), run by the coordinator, with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `mar-plan-2026-11-17-mcp-audit-refresh` and `mar-execution-2026-11-17-mcp-audit-refresh`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
  - Each dispatch writes its own run log; the console goes to a separate console file, never into the run log, and the row reads both tails (Session 88 RULE-2).
- **Queue:** Sessions 74 and 91 run before this one and are committed first. Neither plan changes `mcp-server/` or the audit files (Session 74: `2026-11-14-tts-fp16-phase-guard`, the TTS backend; Session 91: `2026-11-17-e2e-pointer-flakes`, `ui/` E2E specs). Both write the shared closeout files (`known-issues.yaml`, `known-issues.md`, the grouping's §6 table, `current-focus.md`, `metrics.md`). Row 0 checks this (§Sibling overlap).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| All three issues (no MEU) | `.agent/context/handoffs/2026-11-17-mcp-audit-refresh-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-17-mcp-audit-refresh-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-17-mcp-audit-refresh-implementation-critical-review.md`

The session has one handoff, following the no-MEU precedent `2026-11-17-test-run-reliability-handoff.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline, network start condition and plan-local checkers (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py`, `mar-desc-record.json`, the caption and adapter probe receipts |
| WP-2 | The census proof: Red, then Green with the workflow note (rows 1 and 2) | WP-1 | shared | `network-proof.ts`, `run.ts`, `network-proof.test.ts`, `mcp-audit.md` |
| WP-3 | The `avkit_capture` description: Red, Green and the eval rerun (rows 3 to 5) | WP-2 | shared | `capture.ts`, `registry.ts`, `capture-description.test.ts`, `05-mcp-server.md`, the eval receipts |
| WP-4 | The baseline: the coverage Red, then the authoritative run with the update (rows 6 and 7) | WP-3 | shared | `coverage.test.ts`, `baseline-snapshot.json`, `mcp-tool-audit-report.md`, the summary receipts |
| WP-5 | Registers and the grouping row (row 8) | WP-4 | shared | Three issues resolved (two under D-1161, plus any D-1161 or D-1162 issues registered), grouping row 92 |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **You ruled D-1159 A on 2026-11-18** ("A: record all five (Recommended)", relayed by the coordinator): the authoritative run with `--update-baseline` records all five waiting actions (convert probe, and capture crop, frames, sheet and export). That was yours to rule, because the earlier sessions' records say `--update-baseline` needs your words and the grouping makes any tool-shape change in the baseline yours (M-4). Two more briefs, D-1155 (no MEU for the description change) and D-1156 (how the census proof samples), are settled on their recommendation under your hand-over ('orchestrate the plan creation for all sessions and proceed with execution for each', 2026-11-17, continuing 'like we did here. But use the new HDP process.', 2026-11-15); read them if you want to overrule one before execution.
>
> **No stop is held for you during execution.** Under your 2026-11-18 words ("make the decisions always the recommenations"), the two outcomes that used to stop the session each have a recommended action that the executor takes and records in the handoff for you to read afterwards. An audit run that is not clean, or a baseline that fails its check (D-1161): the baseline, report and coverage test go back to their row-0 bytes, the deltas are recorded, each finding is registered as an issue, and the session goes on without the update; the baseline issue stays open. An eval run that completes and fails (D-1162): the description stays as you ruled it, the run is recorded, an issue is registered for the miss, and the session goes on. Neither action edits the baseline by hand or changes the description beyond D-1134 A.
>
> **Two things cost something.** The eval (row 5) runs three fresh Claude Haiku subagents, one per Session 64 task, about 0.5 to 2 million Haiku tokens in all; the coordinator tells you before it starts. The audit (row 7) runs once on this host's network: it downloads its media and a model and reads YouTube, read-only, never uploading, and takes roughly 20 to 40 minutes.
>
> **What changes for you:**
>
> - A model that loads av-kit's tools upfront now reads what `avkit_capture` can do in its description: view a frame with `image`, zoom with a second `sheet` call over a narrower span, and one line per action. The other seven tools read as before. Your IDE's avkit server keeps the old text until you restart it; no row starts, stops or calls it, but the build rewrites `mcp-server/dist/`, which it loads at its next start.
> - A container audit run that hits a flaky network now retries each network proof up to three times before it counts the failure.
> - The committed audit baseline and report now record crop, frames, sheet, export and convert probe as passing on this host.

## Proposed Changes

### Single-statement contracts

- **`NETWORK_PROOF_SAMPLE` (D-1156):** `mcp-server/scripts/audit/network-proof.ts` (new, LF) exports `NETWORK_PROOF_SAMPLES = 3`, `NETWORK_PROOF_GAP_MS = 5000` and `sampleBlocked(once, probes)`, which calls `once()` up to `NETWORK_PROOF_SAMPLES` times, returns `true` at the first call that returns `true`, returns `false` when every call returned `false`, and calls `probes.sleep(NETWORK_PROOF_GAP_MS)` between two calls only (never before the first or after the last). For each URL the row-0 rule's one direct fetch becomes `sampleBlocked` of that fetch: an extract proof holds for a URL when `sampleBlocked(() => probes.extractBlocked(url))` is true, cancel's when `sampleBlocked(() => probes.mediaBlocked(url, wall))` is, and compile's when `sampleBlocked(() => probes.captionsBlocked(url))` is. Each URL is sampled on its own; a member's proof holds only when every one of its URLs holds, as at `:564`.
- **`PROBES_SEAM` (D-1160):** `network-proof.ts` exports `type NetworkProbes = { extractBlocked(url: string): boolean; mediaBlocked(url: string, wall: RegExp): boolean; captionsBlocked(url: string): boolean; sleep(ms: number): void }` and `REAL_PROBES`, whose three probes are the row-0 `youtubeExtractWorks` (negated), `mediaFetchBlocked` and `captionFetchBlocked` moved from `run.ts` with their Python code strings, `cwd: REPO_ROOT` (imported from `./backend.js`), encoding and 180 s timeout unchanged, and whose `sleep` blocks synchronously (`Atomics.wait` on a one-slot `SharedArrayBuffer`), so the census block stays synchronous. `runAudit` passes `REAL_PROBES`; `AuditDeps` does not change, because the tests call `gatherNetworkProof` and `sampleBlocked` directly with fake probes and no AC drives `runAudit` with them (expert pass).
- **`NETWORK_PROOF_GATHER`:** `network-proof.ts` exports `gatherNetworkProof({ mode, fixtures, steps, records, probes })`, returning `Record<string, boolean> | undefined`. It holds the row-0 block's rules (`run.ts:547-577`) unchanged except for the sampling: `undefined` unless `mode === "container"` and `fixtures` is set; only the `ENV_BOUND_AUDIT` members whose step ids are in `NETWORK_STEP_URLS` and that have a failing record matching their signature are probed, plus cancel and compile under their own rules; `undefined` when no key was probed. `run.ts` replaces the block with `const probe = gatherNetworkProof({ ..., probes: REAL_PROBES }); if (probe) env.networkProbe = probe;` and drops its `NETWORK_STEP_URLS` import and the three moved functions; no other line of `run.ts` changes.
- **`FORBIDDEN_IMPORTS_KEPT`:** `network-proof.ts` holds none of the four strings in `tests/audit/forbidden-imports.txt`, in code or comments; `run-cli.test.ts` AC-68.2 passes unchanged.
- **`WORKFLOW_NOTE`:** `.agent/workflows/mcp-audit.md` (CRLF) gains one nested bullet after `:20` (step 3's `- Container: …` bullet), at a five-space indent, so it reads as part of the container run and not as a sixth exit code under step 4 (expert pass): "Each census network proof is tried up to 3 times about 5 s apart and holds when any try is blocked (extract: any failure; cancel: the wall; compile: the retryable caption error). If a network member is still counted, rerun the container audit once before filing it. Authoritative runs gather no proof." The bullet names no CLI flag and is the only line added (`docs.test.ts` cites the flags it finds).
- **`CAPTURE_TOOL_DESCRIPTION` (D-1134 A, D-1157):** `capture.ts` exports `CAPTURE_TOOL_DESCRIPTION`, a string equal byte for byte to `capture-description.expected.txt`, composed from the constants `captureDescriptions` already uses. The flatten, revert and annotate-newline sentences and the four `desc()` marker sentences are hoisted into constants that both read; `FRAMES_TEXT` and `SHEET_TEXT` become arrays joined where they are used; new constants hold only the lead (line 1), the video sentence of line 2 and the method-free `Returns:` sentence of line 4. `registry.ts:172` becomes `avkit_capture: CAPTURE_TOOL_DESCRIPTION,` with the import added to `:17`.
- **`DESC_SHAPE`:** the description is under 4,096 characters; line 1 is the lead ("Call image to view a frame or sheet. To zoom, call sheet again with a narrower start and end; no state is kept between calls."); lines 2 to 5 start `Workflow:`, `Prerequisite:`, `Returns:` and `Errors:`, and no other line starts with one of those markers; lines 6 to 14 start `image: `, `capture: `, `annotate: `, `flatten: `, `revert: `, `crop: `, `frames: `, `sheet: ` and `export: `, in that order.
- **`DESC_TRACE` (D-1157):** each sentence of lines 6 to 14 after its `<action>: ` prefix, split by `/(?<=\.)\s+(?=[A-Z])/`, is a substring of that action's `_meta.action_descriptions` text. So every action line says only what its action text says; only lines 1 to 5 hold condensed text, under D-1134 A.
- **`DESC_PIN`:** `captureDescriptions`, every tool's `_meta.action_descriptions` and every input schema are byte-identical to row 0's `mar-desc-record.json`; the other seven top-level descriptions keep their row-0 SHA-256 (§Acceptance Criteria AC-10). The grouping's "the other seven tools keep their descriptions" holds.
- **`EVAL_RERUN` (D-1158):** the three Session 64 tasks run on the new real surface with Session 64's prompts, harness, media, answer key and checker unchanged, one fresh `general-purpose` subagent with `model: haiku` per task, roots `C:/Temp/av-kit/s64/eval/s92-real-t1/root` to `-t3/root`; `eval-rerun.py check` passes all three. `eval-rerun.py prompts` refuses a describe receipt whose real surface lacks the lead facts, so a stale build cannot be evaluated.
- **`AUDIT_RUN`:** the one authoritative run (row 7) follows `.agent/workflows/mcp-audit.md` steps 2 and 3 (`npm --prefix mcp-server ci`, `uv sync --frozen --all-packages`, `npm --prefix mcp-server run build`, then `npm --prefix mcp-server run audit -- --mode authoritative --baseline <abs baseline> --out <abs dir> --agent claude-code-session-92`), after the host-load wait, and passes `baseline-diff.py summary` with the five `BASELINE_PENDING` keys: exit 0, mode authoritative, commit equal to `HEAD`, cleanup `ok` with no residuals, discovery `pass` with no finding, removed or ghost key, every step `pass`, the `NEW` deltas exactly the five keys and every other delta `UNCHANGED`.
- **`AUDIT_TMP`:** the audit's temp root and `--out` live under `C:/Temp/av-kit/mcp-audit-refresh/`, so no home path reaches its summary or report; the run's own `app-data/mcp-token.txt` is never opened, printed or copied.
- **`BASELINE_RECORD` (D-1159 A, Mat):** row 7's run adds `--update-baseline` and `--report <abs .agent/context/MCP/mcp-tool-audit-report.md>`. The baseline it writes passes `baseline-diff.py baseline` against the row-0 copy: exactly the five keys added, each a plain `{ tool, action, status: "pass" }` entry; every row-0 entry unchanged; none removed; `findings: []`; schema and mode kept; `recorded_commit` equal to `HEAD`; a new `recorded_at`. Neither file is edited by hand.
- **`PENDING_EMPTIED`:** `coverage.test.ts` `BASELINE_PENDING` becomes `[]` in the same change, with the edits named in §Test pins.

### The census proof (rows 1 and 2)

Row 1 writes `network-proof.ts` with `NETWORK_PROOF_SAMPLES = 1`, moves the probes and the block into it, wires `run.ts`, and writes `tests/audit/network-proof.test.ts`. With one sample the move keeps row 0's behaviour, so the runner tests pass while AC-1 to AC-3 fail by assertion. Row 2 sets the constant to 3 and adds the workflow note. The tests drive `gatherNetworkProof` and `sampleBlocked` through fake `NetworkProbes` that count calls and record sleeps; no test spawns `uv`, reaches the network or sleeps for real.

### The `avkit_capture` description (rows 3 to 5)

Row 3 writes `tests/capture-description.test.ts`, which reads the registered tools from `createServer()` (as `m7-resource.test.ts:14-16` does) and needs no new export. Row 4 adds `CAPTURE_TOOL_DESCRIPTION` and the registry line, and one paragraph in `docs/build-plan/05-mcp-server.md` (CRLF) after `:103`: "`avkit_capture`'s top-level description is built from its action text (D-1134 A): the lead says to call `image` to view a frame or sheet and to call `sheet` again over a narrower span to zoom, then the four markers once, then one line per action; it stays under 4,096 characters, `_meta.action_descriptions` is unchanged, and the other tools keep their one-line descriptions." Row 5 reruns the Session 64 eval.

### The coverage Red and the authoritative run (rows 6 and 7)

Row 6 edits `coverage.test.ts` to its post-update expectations, and four tests fail against the row-0 baseline. Row 7 runs `npm ci` and `uv sync` (S10), then the one authoritative audit with `--update-baseline` and the committed report path (Mat's D-1159 A), checks the summary and the written baseline, and runs the coverage tests (all pass). The expert pass cut the earlier no-update run before it: it proves neither change, because the census block runs only in container mode (`run.ts:555`) and discovery reads only the `_meta.action_descriptions` keys (`discovery.ts:26-28`); row 7's update is still guarded by `baseline-diff.py` and the byte restore.

If row 7's audit exits non-0, or its summary or the written baseline fails `baseline-diff.py`, the executor takes D-1161's action and does not stop: the baseline and report go back byte for byte to `baseline-copies/`, `coverage.test.ts` goes back to its row-0 copy (this plan's own edit, so `BASELINE_PENDING` keeps the five keys), the three hashes are checked, `mar-d1161.txt` records the failing checks and every delta, and the session goes on to row 8 without the update. The handoff records AC-12 to AC-14 as not met under D-1161. Neither file is ever edited by hand.

### Registers and the grouping (row 8)

1. `issue-resolve.py` (copied at row 0) sets `status: resolved`, `verification` (today's `last_checked`, a `method` naming the receipts and a `result` quoting their summary lines) and `resolution_path` on the issues it closes, bound to row 0's register hash. Each `resolution_path` starts `Fixed in Session 92 on <date> (plan docs/execution/plans/2026-11-17-mcp-audit-refresh): ` and then says what changed. `meu_links` is kept as it is. `RESOLVE_KEYS` is `status`, `verification`, `resolution_path` and `blast_radius`; `blast_radius` is set only on `MCP-AUDIT-BASELINE-PENDING-CROP`, whose `:5028` text says the pending list holds only `avkit_capture.crop`. Its new `blast_radius`, its `verification.result` (replacing the stale `:5032` "misses only avkit_capture.crop") and its `resolution_path` all name the five keys: `avkit_convert.probe`, `avkit_capture.crop`, `avkit_capture.frames`, `avkit_capture.sheet` and `avkit_capture.export`.
2. Without `mar-d1161.txt`, all three issues are resolved. With it, `MCP-AUDIT-BASELINE-PENDING-CROP` stays open and is not touched; the other two are resolved; and each finding in `mar-d1161.txt` is registered with `tools/issue_triage.py add` (`--component mcp-server`), per `mcp-audit.md` step 5: one issue per non-pass step or discovery finding, or one issue for the run when it left no finding.
3. With `mar-d1162.txt`, one issue is registered for the measured eval miss, citing `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` and the failing runs; the description issue is still resolved, because AC-7 to AC-10 prove the top-level description now carries the action text.
4. `tools/issue_triage.py render` and `render --check`.
5. The grouping's §6 row 92 (`:164`, LF) becomes ``| 92 | `mcp-audit-refresh` | — | P3 | executed (Session 92) | `docs/execution/plans/2026-11-17-mcp-audit-refresh/` |``; no other line changes.

No issue is added when neither record exists. Never hand-edit a generated file.

### Test pins

| Pin | What it checks | After this change |
|---|---|---|
| `tests/audit/coverage.test.ts:23-29` `BASELINE_PENDING` | The five served keys not yet in the baseline | `const BASELINE_PENDING: string[] = [];` with a comment line naming Session 92 and the closed issue (named M-7 edit, D-499's design) |
| `coverage.test.ts:165` `pendingProblems` fixture | A pending key already in the baseline is reported | The call becomes `pendingProblems(["avkit_capture.crop"], baselineKeys, ACTION_SET)` with the expected `["avkit_capture.crop is already in the baseline"]`; the rule under test is unchanged (named M-7 edit) |
| `coverage.test.ts:299-304` "AC-135.19 sheet parity and audit coverage: BASELINE_PENDING ends with the served sheet action" | Sheet waits for the baseline | Retitled "AC-135.19 sheet parity and audit coverage: the committed baseline holds the served sheet action"; asserts `BASELINE_PENDING` is `[]` and the baseline holds `avkit_capture.sheet` (named M-7 edit) |
| `coverage.test.ts:328-332` "AC-136.18 export parity and audit coverage: BASELINE_PENDING ends with the served export action" | Export waits for the baseline | Retitled "AC-136.18 export parity and audit coverage: the committed baseline holds the served export action"; the same shape for `avkit_capture.export` (named M-7 edit) |
| `coverage.test.ts` "AC-68.5 the committed baseline's entries equal AUDIT_ACTION_SET less BASELINE_PENDING and every non-pass carries an issue" and "AC-130.28 the committed baseline misses only the pending keys" | The baseline against the action set | Unchanged text; they fail at row 6 and pass after row 7 |
| `tests/audit/run-cli.test.ts:91-103` AC-68.2 | No script imports the server's toolsets | Unchanged; covers the new `network-proof.ts` |
| `tests/audit/runner-fake-backend.test.ts`, `census-signature.test.ts`, `classify.test.ts`, `transcript-oracle.test.ts` | The runner, the census signatures and the classifier | Unchanged; pass at rows 1 and 2 |
| `tests/audit/docs.test.ts` | The workflow and skill cite real flags | Unchanged; passes with the note |
| `tests/m7-resource.test.ts`, `tests/capture.test.ts` | The 75 per-action texts, their markers and `_meta` | Unchanged; `captureDescriptions` is byte-identical |
| `capture-description.expected.txt` (this folder) | The planned description | Read by `desc-check.mjs`; never changed in execution |

No other existing assertion changes. The four `coverage.test.ts` edits are the ones D-499 designed ("AC-130.28 fails once the baseline holds a pending key", and the `:15-22` comment), named here with their old and new text, so they are not M-7 hits.

### Boundary Inventory

| Boundary | Input | Check |
|---|---|---|
| `gatherNetworkProof` | mode, fixtures, steps, records, probes | Authoritative or no fixtures gives `undefined` and calls no probe (AC-5) |
| `sampleBlocked` | a probe call | At most 3 calls, 2 sleeps (AC-1) |
| `tools/list` | the built server | Description length, shape, trace and pins (AC-7 to AC-10; `desc-check.mjs` on `dist/`) |
| The audit CLI | `--mode authoritative --baseline --out [--update-baseline --report]` | `baseline-diff.py summary` and `baseline` (AC-12, AC-13) |
| The registers | the three issue ids | `issue-resolve.py` bound to row 0's hash (AC-15) |

### Acceptance Criteria

This plan numbers its ACs AC-1 to AC-15 under the Session 92 prefix, as Sessions 78, 79 and 90 did: the new test files use `describe('Session 92 …')`, and each test title starts `AC-<n> ` followed by a space, so `--require AC-1` never matches `AC-10` to `AC-15`.

- AC-1 to AC-3 and AC-7 to AC-9 fail by assertion at their Red rows and pass at Green.
- AC-5 and AC-10 are guards and pass at Red.
- AC-4, AC-6 and AC-12 to AC-15 are checks; AC-11 is the eval; AC-14's coverage tests fail at row 6 and pass at row 7.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-1 | unit (`network-proof.test.ts`, 3 tests) | `NETWORK_PROOF_SAMPLES === 3` and `NETWORK_PROOF_GAP_MS === 5000`; with samples `false, false, true` `sampleBlocked` returns `true` after 3 calls and 2 sleeps of 5000; with all `false` it returns `false` after exactly 3 calls | Spec (issue `:1191` resolution path), D-1156 | Red: 1 sample returns after 1 call |
| AC-2 | unit (2 tests) | Add and transcript: each URL is sampled on its own; a URL blocked only at its second sample lets the proof hold (`false`); a URL that works in all three samples makes it `true`, after 3 calls for that URL | Spec, D-1156 | Red: the proof fails at sample 1 |
| AC-3 | unit (2 tests) | The same for cancel (`mediaBlocked` with cancel's signature) and compile (`captionsBlocked`) | Spec, D-1156 | Red: as AC-2 |
| AC-4 | check | `npm --prefix mcp-server run typecheck`, the build, and `run-cli.test.ts`, `runner-fake-backend.test.ts` and `census-signature.test.ts` pass | Local Canon (`FORBIDDEN_IMPORTS_KEPT`) | A forbidden string in the new file fails AC-68.2 |
| AC-5 | unit, guard (6 tests) | Authoritative mode gives `undefined` and calls no probe; no fixtures gives `undefined`; no failing record that matches the signature gives `undefined`; a failing record with another signature is not probed; the probed keys equal the row-0 rule's for a record set that fails every member; a URL blocked at sample 1 is called once, with no sleep | Local Canon (`run.ts:547-577`), D-1160 | Passes at Red and Green |
| AC-6 | check | `mcp-audit.md` gains exactly the `WORKFLOW_NOTE` line after `:20`, nested under the Container bullet, and stays CRLF; `docs.test.ts` passes | Spec (issue `:1191`) | Any other line diff fails |
| AC-7 | unit (`capture-description.test.ts`) | The registered `avkit_capture` description is under 4,096 characters, line 1 is the lead, and it holds the zoom sentence | Human-approved (D-1134 A) | Red: 145 characters, line 1 is the old text |
| AC-8 | unit | Lines 2 to 5 start with the four markers in order and no other line starts with one; lines 6 to 14 start with the nine action names in `ACTION_INDEX` order | Human-approved (D-1134 A), D-1157 | Red: one line |
| AC-9 | unit | `DESC_TRACE` on lines 6 to 14 against the registered `_meta.action_descriptions` | D-1157 | Red: lines 6 to 14 are missing |
| AC-10 | unit, guard (2 tests), and `desc-check.mjs` | The other seven descriptions keep their row-0 SHA-256 (table below); the registered capture `_meta.action_descriptions` equals `captureDescriptions` with bare keys; after row 4, `desc-check.mjs --baseline <row-0 record> --expected capture-description.expected.txt` passes on `dist/` (capture's description equals the file; the other seven descriptions, every `_meta` and every input schema unchanged) | Human-approved (D-1134 A: "The other seven tools keep their descriptions"), `DESC_PIN` | Passes at Red; `desc-check` fails at row 0 (`mar-plan-desc-check-now.txt`) |
| AC-11 | eval | `eval-rerun.py check` passes all three runs (`run s92-real-t1: pass` to `-t3`) | Human-approved (D-1134 A: "The Session 64 eval tasks are rerun on the new description as the acceptance check"), D-1158 | Session 64's real surface failed t1 and t2 (`mar-plan-eval-session64.txt`) |
| AC-12 | check | Row 7's authoritative run exits 0 and its summary passes `baseline-diff.py summary` (`AUDIT_RUN`): commit `HEAD`, cleanup `ok`, discovery `pass`, every step `pass`, `NEW` exactly the five keys | BASELINE_UPDATE_RULE, `AUDIT_RUN` | A regression, a residual or a sixth `NEW` key fails it |
| AC-13 | check | The baseline row 7 writes passes `baseline-diff.py baseline` against the row-0 copy, and the baseline and report pass `check_home_path.py` | Human-approved (D-1159 A), BASELINE_UPDATE_RULE | An entry changed or removed, or a finding, fails it |
| AC-14 | Red then Green | The `coverage.test.ts` file: the four tests in §Test pins fail by assertion at row 6 (`Tests  4 failed`) and all pass after row 7 | Local Canon (D-499, `coverage.test.ts:15-22`) | Red: the baseline lacks the five keys |
| AC-15 | check | The three issues are `resolved` with `verification` and `resolution_path`, their `meu_links` kept; `MCP-AUDIT-BASELINE-PENDING-CROP`'s `blast_radius`, `verification.result` and `resolution_path` each name all five keys; under D-1161 that issue stays `open` instead and each finding is added as a new issue, and under D-1162 one issue for the eval miss is added; with neither, no issue is added; the render check passes; grouping row 92 reads as planned and no other grouping line changes | Local Canon (`tools/issue_triage*`), D-1161, D-1162 | A hand edit or a second line diff fails it |

**The other seven descriptions at row 0 (AC-10):**

| Tool | Characters | SHA-256 |
|---|---|---|
| `avkit_download` | 91 | `c22a90eba581b02973d531d87ca02ac43fa5226e73ad4c890f01fa257c0496d8` |
| `avkit_transcript` | 98 | `c6b3660065afdc2cc9f36021433c6ff4f1dcd6cd25c90e1137d2c01cbea01379` |
| `avkit_tts` | 109 | `df5d6471a68ba7ed77c54b02db24929ded517cebfe3dd1d61596b78888af1ec7` |
| `avkit_models` | 89 | `2345edcba75c2441a16c92340c70c7979cc0ee92b26a0cdbc7e69000c9bddf41` |
| `avkit_settings` | 107 | `160dfcbbdcd118fd98e8ff890e0e58d5e157c964b209c1b7dbae1d4b4a4b2702` |
| `avkit_health` | 103 | `4c49f8fc874d1ca8131c0fc4f998333bae5bef4c15834dfca71ff079d490583b` |
| `avkit_convert` | 102 | `215e7640860933c37722ba8ab3e959efa8404903f5ca570867a716f2b18bbaaf` |

Row 0 re-derives these into `mar-desc-record.json`; a mismatch with this table is S2.

#### Spec Sufficiency Table

| Question | Answer | Source |
|---|---|---|
| How many samples, how far apart? | 3, about 5 s | Issue `:1191`; D-1156 |
| When does a proof hold? | When any sample is blocked with the signature | D-1156 |
| What may the capture description say? | Its action text, with the repeated sentences removed and the two missed facts first | D-1134 A; D-1157 |
| How long may it be? | Under 4,096 characters | D-1134 A |
| What is the acceptance check? | The Session 64 tasks rerun | D-1134 A; D-1158 |
| Which baseline rows are added? | The five served `BASELINE_PENDING` keys | `coverage.test.ts:15-22`, issue `:5021`; Mat's D-1159 A |
| What if the run or the baseline check fails? | Restore, record, register and go on without the update | D-1161, under Mat's 2026-11-18 words |
| What if an eval run fails? | Keep the description, record, register and go on | D-1162, under Mat's 2026-11-18 words |
| Who writes the baseline? | The audit run itself | BASELINE_UPDATE_RULE, `mcp-audit.md` exit criteria |

#### Files Modified

| Path | Change | Row |
|---|---|---|
| `mcp-server/scripts/audit/network-proof.ts` | New | 1, 2 |
| `mcp-server/scripts/audit/run.ts` | The probes and the census block moved out; the call passes `REAL_PROBES` (`AuditDeps` unchanged) | 1 |
| `mcp-server/tests/audit/network-proof.test.ts` | New | 1 |
| `.agent/workflows/mcp-audit.md` | One nested line after `:20` | 2 |
| `mcp-server/tests/capture-description.test.ts` | New | 3 |
| `mcp-server/src/toolsets/capture.ts` | `CAPTURE_TOOL_DESCRIPTION` and the hoisted constants | 4 |
| `mcp-server/src/toolsets/registry.ts` | `:17` import, `:172` | 4 |
| `docs/build-plan/05-mcp-server.md` | One paragraph after `:103` | 4 |
| `mcp-server/tests/audit/coverage.test.ts` | The four §Test pins edits (back to row 0 under D-1161) | 6, 7 |
| `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` | Written by the audit (row-0 bytes under D-1161) | 7 |
| `.agent/context/MCP/mcp-tool-audit-report.md` | Written by the audit (row-0 bytes under D-1161) | 7 |
| `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` | Through `issue-resolve.py`, `issue_triage.py add` (only under D-1161 or D-1162) and `render` | 8 |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | Row 92 | 8 |
| The handoff, the reviews, the reflection, `docs/execution/metrics.md`, `.agent/context/current-focus.md` | Closeout | H1, H2 |

Read, never changed: `mcp-server/scripts/audit/census.ts`, `plan.ts`, `classify.ts`, `backend.ts`, `mcp-server/tests/audit/run-cli.test.ts`, `runner-fake-backend.test.ts`, `census-signature.test.ts`, `classify.test.ts`, `transcript-oracle.test.ts`, `docs.test.ts`, `forbidden-imports.txt`, `mcp-server/tests/m7-resource.test.ts`, `capture.test.ts`, `fixtures.ts`, `.agent/skills/mcp-tool-audit/SKILL.md`, and the Session 64 files `eval-run.md`, `eval-harness.ts`, `eval-check.py` and `eval-seed.py`.

**Line endings** (measured with Python bytes, `mar92-probe.txt`): `run.ts`, `census.ts`, `registry.ts`, `capture.ts`, `coverage.test.ts`, `docs.test.ts`, `census-signature.test.ts`, `transcript-oracle.test.ts`, `classify.test.ts`, `m7-resource.test.ts`, `fixtures.ts`, `SKILL.md`, `mcp-audit.md`, `05-mcp-server.md`, `current-focus.md` and `metrics.md` are CRLF and stay CRLF; edit them with `newline=""` from CRLF text. `baseline-snapshot.json` is CRLF at row 0 and the audit writes it as LF; that is the tool's output and is not converted back (`eol-check.py` expects LF for it after row 7, or CRLF when D-1161 restored the row-0 bytes). The audit report, `known-issues.yaml`, `known-issues.md`, the grouping and the Session 64 eval files are LF. The three new files are LF. `eol-check.py` checks every scope path.

### Project files

- `.agent/context/current-focus.md` (H1-3; CRLF; read first, another session may have written it).
- `docs/execution/metrics.md` (H2-3; CRLF).
- No `meu-status.yaml` change; `tools/meu_status.py render --check` runs at H1-3 and H2-2.

### Sibling overlap

| Session | Plan | Shared files | Row 0 checks |
|---|---|---|---|
| 74 (`tts-fp16-phase-guard`) | `docs/execution/plans/2026-11-14-tts-fp16-phase-guard/` | `known-issues.yaml`, `known-issues.md`, the grouping's §6, `current-focus.md`, `metrics.md` | No commit since `ecfa3f3` touches `mcp-server/`, `.agent/skills/mcp-tool-audit/`, `.agent/context/MCP/`, `.agent/workflows/mcp-audit.md` or `docs/build-plan/05-mcp-server.md`; the three issues are still `open`; row 92 is still `proposed` |
| 91 (`e2e-pointer-flakes`) | `docs/execution/plans/2026-11-17-e2e-pointer-flakes/` | The same closeout files | The same |
| 93, 94 | Later | The same closeout files | Not run yet |

A moved citation is fixed in the handoff (Session 51 RULE-3); a removed anchor, a touched audit path or a changed issue state is S2.

## Out of Scope

| Item | Why |
|---|---|
| The other seven tools' descriptions | D-1134 A: "the other seven tools keep their descriptions until a miss is measured"; any change goes back to Mat |
| A container audit run | The Windows host runs authoritative mode; the unit tests prove the sampling |
| `SKILL.md` text | The issue names only `mcp-audit.md` for the note |
| `_meta.action_descriptions` and input schemas | D-1134 A keeps them |
| An MEU | D-1155 |
| Any `issue` field on a baseline entry | Every entry passes; BASELINE_ANNOTATION_RULE has nothing to set |
| An authoritative run with no update before the update run | Cut by the expert pass: it proves neither change, since the census block runs only in container mode (`run.ts:555`) and discovery reads only the `_meta` keys (`discovery.ts:26-28`); it would cost a 20 to 40 minute network run, and the update run is guarded by `baseline-diff.py` and the byte restore (D-1161) |
| A hand edit of the baseline or report, or a description change beyond D-1134 A | Never, under D-1161 and D-1162 either |

## BUILD_PLAN.md Audit

No MEU, so no `docs/BUILD_PLAN.md` row and no `meu-status.yaml` change. `docs/build-plan/05-mcp-server.md` §Descriptions (M7) gains the paragraph in row 4. `docs/build-plan/09-screenshot-capture.md` near `:1247` (the Session 64 eval) is read and not changed.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`, in the shape of `2026-11-17-queue-convert-fixes/baseline.ps1`, records:

- `HEAD` (`baseline.sha`), `git status --porcelain --untracked-files=all` (`baseline-dirty.txt`, with each path's SHA-256 in `baseline-dirty-hashes.json`), `git worktree list` and the host load;
- the commits since `ecfa3f3` that touch the audit paths (§Sibling overlap), naming Sessions 74 and 91; any is S2;
- `baseline-scope.json` (each §Files Modified and "Read, never changed" path to its SHA-256 or `absent`; the three new files and the handoff must be `absent`), `baseline-eol.json`, and `baseline-skip-hashes.json` (every tracked or untracked, not-ignored file under `packages/`, `tools/`, `ui/` and `tests/`);
- byte copies of each scope file under `C:/Temp/av-kit/mcp-audit-refresh/baseline-copies/<path>`, and `C:/Temp/av-kit/mcp-audit-refresh/tmp`;
- the S2 binding: the anchors in `mar92-probe.txt` re-read by line and text, the three issues `open`, `YOUTUBE-CAPTIONS-IP-BLOCK` `resolved`, grouping row 92 `proposed`;
- the start condition (grouping §5): `caption_probe.py` and `adapter_probe.py` from this folder, the triage's caption and adapter probes; either printing `FAIL` is S2 and the session waits;
- the MCP build and `desc-check.mjs --record mar-desc-record.json` (the row-0 descriptions, `_meta` and schemas), checked against the AC-10 table;
- the base receipts: `npm --prefix mcp-server run typecheck` and the full MCP Vitest run (pwsh, `Set-Location 'P:\av-kit\mcp-server'`, `npx vitest run`), failures recorded, not fatal;
- the copies of `red-check.py`, `identity.py`, `issue-resolve.py` and `eol-check.py` from `2026-11-17-queue-convert-fixes/` (§task row 0 lists the settings), their selftests, the `desc-check.mjs`, `eval-rerun.py` and `baseline-diff.py` selftests, `eval-rerun.py --session64`, and `ruff format --check` and `ruff check` on this folder's Python (Session 82 RULE-1).

The scope walk drops the secret paths and `.agent/fleet/hub` before any stat (Session 83 RULE-2).

### 2. Red, then Green

| Red | Fails | Passes | Green |
|---|---|---|---|
| Row 1 | AC-1 to AC-3 (7 tests) | AC-5 (6 tests); the runner tests | Row 2 (13 tests; AC-4, AC-6) |
| Row 3 | AC-7 to AC-9 (3 tests) | AC-10 (2 tests) | Row 4 (5 tests; `desc-check`) |
| Row 6 | The four coverage tests | The rest of `coverage.test.ts` | Row 7 (all; under D-1161 the file is back at row 0 and AC-14 is recorded not met) |

`red-check.py` reads each Red receipt and its `.exit` file and refuses exit 0, setup failures and non-assertion diagnostics. `DECLARED_NEW` is `NETWORK_PROOF_SAMPLES`, `NETWORK_PROOF_GAP_MS`, `sampleBlocked`, `gatherNetworkProof`, `REAL_PROBES` and `CAPTURE_TOOL_DESCRIPTION`. Expectations stay immutable in Green: rows 1, 3 and 6 record the SHA-256 of the test files they write, and rows 2, 4 and 7 check them (S3).

### 3. Eval and audit proofs (rows 5 and 7)

- **Eval (row 5).** Build; describe into `mar-eval-describe.txt` from a fresh root `C:/Temp/av-kit/s64/eval/s92-describe/root`; seed the three roots (t3 with `dashboard-4k.png`); `eval-rerun.py prompts --describe`; then one fresh subagent per task with the prompt file's text alone, its final message saved unedited to `C:/Temp/av-kit/mcp-audit-refresh/mar-eval-real-tN-report.txt`; then `eval-rerun.py check`. The harness starts the isolated real backend over each root (execution note, Session 92: the reviewed plan said a fake backend; the harness starts the isolated real `spawnBackend`, eval-harness.ts:30,78-85,99-107; plan review non-blocking note). A run that ends with a harness or subagent error and no report is rerun once from a fresh root; a run that completes and fails takes D-1162's action (S9), which writes `mar-d1162.txt` and goes on.
- **Audit (row 7).** `AUDIT_RUN`, `AUDIT_TMP`, `BASELINE_RECORD`, then `baseline-diff.py summary` and `baseline`. The summary is read from `<out>/mcp-audit-summary.json`; the out folder is `C:/Temp/av-kit/mcp-audit-refresh/audit-r7`. A failing run or check takes D-1161's action (S7, S8), which writes `mar-d1161.txt` and goes on.

### Session gate (H1-2)

`session-gate.ps1`, in the shape of `2026-11-17-queue-convert-fixes/session-gate.ps1`, fail-fast, later steps printed `not_run`, last line `session-gate: all steps exit 0`:

| Stage | Steps |
|---|---|
| Identity | `identity-before` (`identity.py`, which clears `ELECTRON_RUN_AS_NODE`) |
| Static | `mcp-types`; `task-contract`; `scope-paths`; `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `red-check-selftest`, `eol-check-selftest`, `desc-check-selftest`, `eval-rerun-selftest`, `baseline-diff-selftest`; `py-format` and `py-lint` on this folder's Python; `desc-check-syntax` (`node --check desc-check.mjs`) |
| Targeted | `mcp-unit` (`network-proof.test.ts`, `capture-description.test.ts`, `coverage.test.ts`, `docs.test.ts`, `run-cli.test.ts`); `desc-check` (`--baseline mar-desc-record.json --expected capture-description.expected.txt`); `baseline-diff` (`baseline` against the row-0 copy; when `mar-d1161.txt` exists, a byte check of the baseline, report and `coverage.test.ts` against their row-0 copies instead) |
| Host load | `host-load`: five `Win32_Processor.LoadPercentage` samples; above 50 % it waits, re-sampling every 30 s for up to 10 minutes, and records the value it ran at |
| Fresh full | `mcp-build`, `mcp-tests` (full Vitest in `mcp-server/`; it excuses only ids the base receipt shows failing), `issues-render-check`, `state-render` |
| Identity | `identity-after` |
| Skipped, with reasons | `py-tests`, `py-types`, `ui-types`, `ui-lint`, `ui-tests`, `ui-build`, `ui-electron` and `openapi`: every `packages/`, `tools/`, `ui/` and `tests/` file keeps its `baseline-skip-hashes.json` hash (H1-4); `mcp-audit`: run authoritatively at row 7 on this tree, and a second network run adds nothing |

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` appears | Stop; re-plan the context tool decision |
| S2 | A cited anchor is gone or changed in meaning, an audit path was touched since `ecfa3f3`, an issue is not `open`, row 92 is not `proposed`, the AC-10 table does not match row 0, or a caption or adapter probe prints `FAIL` | Stop; a moved line only is fixed in the handoff (Session 51 RULE-3); a caption block means the session waits (grouping §3) |
| S3 | A Red fails for a setup reason or passes, or a Green needs an expectation change | Stop; never edit the test to pass |
| S4 | `git status` lists a path outside this plan's scope and `baseline-dirty.txt`, or a scope path no earlier row wrote differs from `baseline-scope.json` | Stop and ask Mat; never commit, stash or revert another session's work |
| S5 | An existing test that passed in the base receipt fails | Stop (M-7); never change it outside §Test pins |
| S6 | Codex is unavailable or the ledger refuses a round | Mat |
| S7 | Row 7's run fails `baseline-diff.py summary` (exit not 0, a residual, a `REGRESSION`, `REMOVED`, `KNOWN` or `FIXED` delta, or a `NEW` key beyond the five) | Take D-1161, do not stop: restore the baseline, report and `coverage.test.ts` from `baseline-copies/`, check the hashes, write `mar-d1161.txt` with the failing checks and deltas, register each finding at row 8 (`mcp-audit.md` step 5), leave the baseline issue open, go on without the update. A run that dies on an infrastructure error with no summary (S10's held file, a crashed spawn) is rerun once before D-1161 is taken |
| S8 | Row 7's update is refused (exit 2) or the written baseline fails `baseline-diff.py baseline` | Take D-1161, as in S7 |
| S9 | An eval run completes and fails `eval-rerun.py check` | Take D-1162, do not stop: keep the description (never change it beyond D-1134 A), write `mar-d1162.txt` naming the failing runs, keep the prompts, ledgers and reports for the handoff, register one issue at row 8, record AC-11 not met, go on |
| S10 | `npm ci`, `uv sync` or the build fails with `EPERM` or `EBUSY` | Tell Mat which file is held; never stop a process |
| S11 | `check_home_path.py` finds a home path | Stop; fix the writer, never the check |
| S12 | A `packages/`, `tools/`, `ui/` or `tests/` file changed, was added or was removed since row 0 | Stop; the skips lose their basis |
| S13 | At Green the description is 4,096 characters or more, or fails `DESC_TRACE` | Stop; a description change outside D-1134 A goes back to Mat |

## Decision Log

> [!NOTE]
> D-1157, D-1158 and D-1160 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-1155 hit M-8 and D-1156 hit M-3 and M-6, so they are briefs (below), handed to the agent. D-1159 hit M-4 and M-6 and is Mat's: he ruled A on 2026-11-18 (`resolution: human`, `source_tag: Human-approved`, relayed by the coordinator). The expert pass found the M-4 hit: the earlier sessions' records say `--update-baseline` needs Mat's words, and grouping `:106` makes any tool-shape change in the baseline his. AC-13 rests on that ruling and carries its tag. D-1161 and D-1162 hit M-8 (each continues with ACs not met) and are handed to the agent under Mat's 2026-11-18 words; their actions never edit the baseline by hand and never change the description beyond D-1134 A. The §4a check found no other M item. M-4 otherwise: D-1134 A is Mat's ruling on the description; the input schemas, `_meta` and the other seven descriptions stay byte-identical (AC-10). M-7: the four `coverage.test.ts` edits are named in §Test pins with their old and new text, as D-499 designed them. M-2: no user data is read or written; the audit runs its own backend in a scratch root. The Haiku spend in D-1158 is the acceptance check Mat named in D-1134 A, and the coordinator tells Mat before it runs. `open_decisions` is empty and there is no STOP item for Mat in execution; D-1163 and D-1164 are left free for execution.
>
> **Why Session 92 is inside the hand-overs.** Mat's 2026-11-17 message asked to "orchestrate the plan creation for all sessions and proceed with execution for each. Use same approach as we did in the last session grouping run", continuing his 2026-11-15 hand-over ('like we did here. But use the new HDP process.'), and Session 92 is §3 of the grouping that message names (this plan's `grouping_source`). That message is dated 2026-11-17, the same day as this brief set, so the hand-over is not carried from an earlier brief set (HDP §6 scopes a hand-over to one brief set), and `plan_to_exec_gate: human` puts the briefs in front of Mat again before execution. D-1155's and D-1156's reasoning starts with the same sentence, word for word: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'." On 2026-11-18, relayed by the coordinator for this brief set, Mat said: "Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!" D-1161's and D-1162's reasoning starts with that sentence as `Handed to the agent: USER_EXPLICIT 2026-11-18 '…'.`, and each action is recorded in the handoff for Mat to read afterwards.
>
> **Earlier rows are not copied here.** The grouping rows D-1131 to D-1134 live in the grouping file's §8, and D-499 in `MCP-AUDIT-BASELINE-PENDING-CROP`'s decision log. H2-2 reads them through `--decision-source` on the grouping and on `.agent/context/known-issues.yaml`, with `--decision-issue` for `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` and `MCP-AUDIT-BASELINE-PENDING-CROP` only. `decision_sources` was probed at plan time against this plan itself, with the H2-2 validator's own source list (Session 90 RULE-2; `mar92-probe.txt`, rerun after this plan was written): the grouping alone gives D-1131 to D-1134; with the register and those two issues it adds D-499; with `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` as a third `--decision-issue` the validator refuses, because that issue records D-1134 at the `triage` stage and the grouping records it at the `grouping` stage. D-1134 is still read from the grouping, so H2-2 leaves that issue out of `--decision-issue`. Under HDP §6 the reflection's `### Decisions Log` lists only this session's reversible autonomous choices.

```yaml
decision_log:
  - id: D-1155
    stage: planning
    question: "Does the avkit_capture description change need an MEU?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "A: no MEU. The description change runs under MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL with the Session 92 AC prefix; its ACs, Red and Green rows, eval and review are this plan's."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:41 — 'The Session 92 plan decides whether it needs an MEU': the grouping left the question open"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:189 §8 D-1132 — no MEU for test or tooling debt; a plan registers one if a cause is in the product"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md §8 D-1134 — Mat's ruling A on this exact string and where it lands (Session 92, before its baseline)"
      - ".agent/context/meu-status.yaml:3433-3435 — MEU-131 is gui-capture-crop-tool; known-issues.yaml:5145 links it only because Session 60 found the issue"
      - "docs/execution/plans/2026-11-17-test-run-reliability/implementation-plan.md — Session 90, the no-MEU shape"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-8 because the choice is whether to add an MEU, and the grouping left it to this plan (:41). D-1132's test (:189) asks for an MEU when a cause is in the product, and this cause is: the top-level description is product text. But an MEU exists to carry a product decision through a build-plan row and an AC family, and Mat's D-1134 A has already made the product decision on this exact string: what it may say, its limit and its acceptance check. There is no new behaviour, endpoint, schema or action. MEU-131 (gui-capture-crop-tool) does not own capture's action text; the issue names it only because Session 60 found the gap there. A new MEU (B) would add a build-plan row, a status entry and an AC family for one string, with the same tests and eval this plan already runs, so it adds bookkeeping and no decision. Two-way: an MEU can be registered later through tools/meu_status.py."
  - id: D-1156
    stage: planning
    question: "How does the census network proof sample, and when does it hold?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-3, M-6]
    chosen: "A: each URL's direct fetch is tried up to 3 times about 5 s apart (NETWORK_PROOF_SAMPLES = 3, NETWORK_PROOF_GAP_MS = 5000), stopping at the first sample that is blocked; the proof holds for a URL when any sample is blocked (extract: any failure; cancel: the wall; compile: the retryable caption error), and for a member when every one of its URLs holds. Container mode only; the authoritative mode gathers no proof. mcp-audit.md gains one note nested under step 3's Container bullet."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:1191 — MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT: sample up to 3 times; 'proof holds only if every sample fails with the signature'; add a re-run note"
      - "mcp-server/scripts/audit/run.ts:547-577 — the one-shot proof; :564 a member's proof holds only when every URL fails a direct extract"
      - "mcp-server/scripts/audit/run.ts:364, :385, :407 — what blocked means per probe: extract any non-zero exit, cancel exit 3 with the wall, compile exit 3 (the retryable caption error)"
      - "mcp-server/scripts/audit/census.ts — a proof holds when env.networkProbe[key] === false"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-3 because the sample count and gap set how hard the audit tries before it counts a failure; M-6 because the issue's words conflict with its own symptom. The issue's failure is a proof that one lucky fetch got through while the audit's own call was blocked. Under its literal rule (B, every sample must be blocked), more samples make that worse: each extra sample is another chance for one fetch to get through, so the proof fails more often, not less. A (any sample blocked) is what fixes the symptom the issue describes: a single blocked sample shows that the network refuses the fetch at times, which is the environment fact the census needs. Blocked keeps each probe's own test from run.ts: only cancel's probe reads a signature (the wall); extract counts any failure and compile the retryable caption error. C (keep one shot and add only the note) leaves the symptom. 3 samples and 5 s come from the issue; a URL costs at most 3 times its 180 s timeout, in container mode only. Two-way: one constant."
  - id: D-1157
    stage: planning
    question: "How is the avkit_capture top-level description put together?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Line 1 is the lead (call image to view a frame or sheet; call sheet again with a narrower start and end to zoom); lines 2 to 5 carry the four markers once each, from the old top-level Workflow line, desc()'s shared Prerequisite and Errors sentences, a method-free Returns sentence and a short video workflow taken from frames' Workflow sentence; lines 6 to 14 hold one line per action that adds its own text, in ACTION_INDEX order, each made only of that action's own sentences with the shared marker sentences, frames' and sheet's own Workflow and Errors lines, sheet's Prerequisite and zoom sentences (already in the lead) and image's annotation example (kept on annotate) left out. 3,981 characters (capture-description.expected.txt). DESC_TRACE holds every action line to its _meta text."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md §8 D-1134 — A: a real description built from the existing action text, the repeated sentences removed, the missed facts first, under 4,096 characters"
      - "mcp-server/src/toolsets/capture.ts:33-94 — desc(), the action constants and captureDescriptions"
      - "C:/Temp/av-kit/s64-E4-check.txt — Session 64: t1 made no image call; t2 made one sheet call where two were needed"
      - "C:/Temp/av-kit/mcp-audit-refresh/mar92-trace-probe.txt — DESC_TRACE holds on the expected file"
    research: { engine: none, sources: [] }
    reasoning: "D-1134 A fixes the content: the existing action text, with the sentences every action repeats removed and the two missed facts first, under 4,096 characters. What is left is layout. One line per action keeps each fact next to its action's name, so a model can find it; the markers once at the top keep the M7 rule (05 §Descriptions) for the tool as a whole. The only condensed text is in lines 1 to 5, and every action line is traceable to _meta (DESC_TRACE), so no sentence says something the action text does not. 3,981 characters leaves room under the limit. The eval (D-1158) is the acceptance check. Two-way: one constant."
  - id: D-1158
    stage: planning
    question: "How is the Session 64 eval rerun as the acceptance check?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Session 64's real surface only, with its prompts, harness, media, answer key and checker unchanged: describe from the new build, seed three fresh roots, one fresh general-purpose subagent with model haiku per task, then eval-rerun.py check; all three runs must pass. The coordinator tells Mat before it runs (about 0.5 to 2 million Haiku tokens). A run that ends in an infrastructure error with no report is rerun once from a fresh root; a run that completes and fails takes D-1162's action (keep the description, record, register an issue, go on)."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md §8 D-1134 — 'The Session 64 eval tasks are rerun on the new description as the acceptance check'"
      - "docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md — Session 64's procedure (D-608)"
      - "C:/Temp/av-kit/mcp-audit-refresh/mar-plan-eval-session64.txt — Session 64's real result reproduced at plan time"
    research: { engine: none, sources: [] }
    reasoning: "Mat named the acceptance check. Session 64 ran one subagent per task on Haiku, so the same harness, the same model and one run per task make the result comparable with its real-surface failures. The meta surface is not rerun: it is not what a model loading tools upfront sees. The harness starts the isolated real backend over its own root with local media (execution note, Session 92: the reviewed plan said a fake backend; plan review non-blocking note), so the only cost is the Haiku tokens, which the coordinator announces. Three runs at one per task can still pass by chance; that is the measure Mat chose."
  - id: D-1159
    stage: planning
    question: "May Session 92 run --update-baseline to record all five already-approved rows (convert.probe; capture crop, frames, sheet, export)?"
    resolution: human
    class: one-way-door
    mandatory: [M-4, M-6]
    chosen: "A: record all five (Recommended) — the five BASELINE_PENDING keys (avkit_convert.probe, avkit_capture.crop, avkit_capture.frames, avkit_capture.sheet, avkit_capture.export), each as a plain pass entry written by the authoritative run itself; every row-0 entry unchanged; BASELINE_PENDING emptied in the same change."
    source_tag: Human-approved
    human_message_reference: "USER_EXPLICIT 2026-11-18 AskUserQuestion 'A: record all five (Recommended)'"
    precedents:
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:106 — the Gate rule: any tool-shape change in the baseline is Mat's (M-4)"
      - ".agent/context/handoffs/2026-11-10-video-probe-frames-MEU-133-handoff.md:289, 2026-11-10-video-probe-frames-MEU-134-handoff.md:347, 2026-11-11-capture-video-sheet-MEU-135-handoff.md:365, 2026-11-11-capture-export-copy-MEU-136-handoff.md:361 — --update-baseline needs Mat's words"
      - "mcp-server/tests/audit/coverage.test.ts:15-22 — the next authoritative update 'adds them, empties this list and closes MCP-AUDIT-BASELINE-PENDING-CROP'; MEU-133 to MEU-136 each added their key 'on the same terms'"
      - ".agent/context/known-issues.yaml:5021 — closed by the next authoritative update, which 'records avkit_capture.crop and empties BASELINE_PENDING in the same change'"
      - "mcp-server/scripts/audit/run.ts:590-610 — the update writes one entry per served action"
      - ".agent/workflows/mcp-audit.md — exit criteria: the baseline is updated by the run itself, never by hand"
    research: { engine: none, sources: [] }
    reasoning: "Mat ruled A on 2026-11-18 by AskUserQuestion in the coordinator session, relayed by the coordinator to this plan. M-4 because the earlier sessions' records say --update-baseline needs Mat's words (the MEU-133 to MEU-136 handoffs and plans) and grouping :106 makes any tool-shape change in the baseline Mat's; the expert pass found this, so the brief was not the agent's to settle. M-6 because the sources differ in their words: grouping :104 and the issue's notes (known-issues.yaml:5040) name crop alone, while the test that holds the list says the update adds all of them and empties it, and the issue says the update empties BASELINE_PENDING, which only all five can do. The planning reasoning, kept: the update cannot write crop alone: it records every served action, so B (crop only) would need a hand edit of the baseline, which the workflow forbids, and would leave AC-68.5 failing. The four other rows add no tool shape: each action is already served, and each was approved and added to BASELINE_PENDING on these terms by its own MEU (133 to 136). The baseline is a contract record, so the update is one-way in the sense that it becomes the reference for later regressions; baseline-diff.py and D-1161's restore keep it from recording anything but the five new passes."
  - id: D-1160
    stage: planning
    question: "How do the tests reach the census probes without the network?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "PROBES_SEAM: the probes and the census block move to scripts/audit/network-proof.ts with a NetworkProbes type and REAL_PROBES; gatherNetworkProof takes probes, run.ts passes REAL_PROBES, AuditDeps is unchanged, and the tests call gatherNetworkProof and sampleBlocked with fakes."
    source_tag: Local Canon
    precedents:
      - "mcp-server/scripts/audit/run.ts:102-107 — AuditDeps (launcher, steps, platform, mutateLaunch), left unchanged because no AC drives runAudit with fake probes"
      - "mcp-server/scripts/audit/run.ts:549-550 — the default test suite never touches YouTube (05 §Testing)"
      - "mcp-server/tests/audit/run-cli.test.ts:91-103 — scripts must not import the server's toolsets"
    research: { engine: none, sources: [] }
    reasoning: "The probes spawn uv and reach YouTube, so the tests need fakes. A separate module whose entry takes the probes as an argument keeps run.ts's change to a few lines and lets the tests call gatherNetworkProof directly, with no backend; an AuditDeps.probes seam would only serve a runAudit test no AC asks for, so the expert pass cut it. A synchronous sleep keeps the block as it is (synchronous spawnSync calls), so no await is added to runAudit. Two-way."
  - id: D-1161
    stage: planning
    question: "What does the executor do when row 7's authoritative run is not clean, or its update is refused or the written baseline fails its check (S7, S8)?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "Restore and continue: put the baseline and report back byte for byte from baseline-copies, put coverage.test.ts back to its row-0 copy (this plan's own edit, so BASELINE_PENDING keeps the five keys), check the three SHA-256 values against row 0, write mar-d1161.txt with the failing checks and every delta, register at row 8 one issue per non-pass step or discovery finding (or one issue for the run when it left no finding) with tools/issue_triage.py add and render, per mcp-audit.md step 5, leave MCP-AUDIT-BASELINE-PENDING-CROP open, and go on without the update; the handoff records AC-12 to AC-14 as not met under D-1161 for Mat to read. A run that dies on an infrastructure error with no summary is rerun once first. Never hand-edit the baseline or report."
    source_tag: Local Canon
    precedents:
      - ".agent/skills/mcp-tool-audit/SKILL.md — BASELINE_UPDATE_RULE: the baseline is written only by a clean run"
      - ".agent/workflows/mcp-audit.md step 5 — file every finding with issue_triage.py add, then render"
      - "docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md:330 — pending keys and their issue wait for the next authoritative update; this action keeps them waiting"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:106 — --update-baseline only from a clean authoritative run with no regression (BASELINE_UPDATE_RULE)"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!'. M-8 because the action continues the session with AC-12 to AC-14 not met, which changes what the session accepts. Restoring keeps the committed baseline as the last clean contract record, so nothing one-way happens: no baseline is written by hand and no failing run is recorded. Registering each finding is what the workflow asks of any audit, so the failure is tracked, not lost. Stopping (the old reservation) would leave the tree with a half-written baseline and wait on Mat for an action that has one sensible answer. B (rerun until it passes) hides a real regression and is refused. Two-way: a later session reruns the audit and records the five keys."
  - id: D-1162
    stage: planning
    question: "What does the executor do when an eval run completes and fails eval-rerun.py check (S9)?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "Keep and continue: keep the description as D-1134 A built it (never change it beyond D-1134 A), write mar-d1162.txt naming the failing runs, keep each run's prompt, ledger and report for the handoff, register at row 8 one issue for the measured miss that cites MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL, still resolve that issue because AC-7 to AC-10 prove the top-level description now carries the action text, record AC-11 as not met in the handoff for Mat to read, and go on."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md — no description text changes without Mat's words"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md §8 D-1134 — 'the other seven tools keep their descriptions until a miss is measured'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!'. M-8 because the action continues with AC-11 not met. The description is Mat's ruling, so a failing eval cannot change it; what is left is to record the miss so a later ruling has the measurement, which the new issue holds. The description issue's gap (the model never sees the action text) is closed by the change itself, which AC-7 to AC-10 prove; how well the text works is the new issue's question. Stopping would hold a finished change for a result that changes nothing in this session. Two-way: the new issue carries the next step."
  - id: D-1163
    stage: execution
    question: "Register a known issue for the Session 64 eval-harness describe capture, which decodes the server's UTF-8 through cp437 (D-1186)?"
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "A: register at row 8 one issue, through tools/issue_triage.py add and render, for the Session 64 eval tooling's describe capture: eval-run.md step 3 and task.md row E-1 redirect native output in PowerShell, which decodes the UTF-8 through cp437 and writes CRLF, so the surface a model reads has mojibake arrows and dashes. It records that Session 64's eval ran on that corrupted surface, that Session 92 re-captured raw bytes and guards its own prompts path (eval-rerun.py), and that the fix (a raw-bytes capture and a fail-closed check in the Session 64 files) is left for a later session. Nothing in Session 64's files changes in this session."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md:24 — step 3 captures describe with a shell redirect"
      - "docs/execution/plans/2026-11-11-capture-export-copy/task.md:63 — row E-1 runs it as rtk proxy npx tsx ... describe *> s64-E1-describe.txt"
      - "C:/Temp/av-kit/mcp-audit-refresh/mar-eval-d1186-roundtrip.txt — the attempt1 receipt and prompts are the raw bytes decoded through cp437"
      - "AGENTS.md:33 — known-issues.yaml is the SSOT, changed only through issue-triage"
      - "docs/execution/plans/2026-11-17-mcp-audit-refresh/implementation-plan.md D-1162 — row 8 registers what the eval measures, so the register holds the measurement for a later ruling"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.', and USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: A registers one issue; B (do nothing) leaves the defect recorded only in this session's handoff; C fixes Session 64's eval-run.md and task row now. C is refused: those files are another session's evidence, outside this plan's Files Modified, and the brief forbids editing them. B loses the finding: the handoff is read once, while the next eval that follows eval-run.md step 3 repeats the corruption, and the question whether Session 64's AC-136.19 result still holds on clean text stays with no owner. A puts the defect where the workflow keeps open work (AGENTS.md:33) at the row the plan already uses for registering, and changes no test, threshold, AC or file outside the register. No M item is hit: M-8 covers adopting a finding as new scope, and an issue that records a defect for later is a tracking row, not a fix in this session's acceptance; M-7 and M-11 are untouched because no test or gate changes. Two-way: the issue can be closed or merged by issue-triage at any time."
  - id: D-1164
    stage: execution
    question: "Row 8's final check cannot see MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL's resolution_path, because its block slice stops at the issue's first decision_log entry. How is row 8 proved?"
    resolution: autonomous
    class: two-way
    mandatory: []
    chosen: "A: keep the failing mar-row8-check.txt, and rerun the row's own final check, taken from task.md at run time, with one change: blk cuts at the next issue (a newline, two spaces and '- id: ') instead of the first '- id: ' (tmp/row8-check-fixed.py asserts that the old blk text occurs once and replaces only it). Mark row 8 on that receipt (mar-row8-check-d1164.txt) and disclose it in the handoff. The plan's command, the register and every other clause stay as they are."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-17-mcp-audit-refresh/task.md row 8 — the check's blk slice and its clauses"
      - "C:/Temp/av-kit/mcp-audit-refresh/baseline-copies/.agent/context/known-issues.yaml:5191 — the issue's resolution_path sat after enrichment at row 0"
      - ".agent/docs/human-decision-protocol.md M-3 — a mechanical repair under existing policy is not an M-3 hit"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.', and USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: A reruns the row's check with only the block boundary fixed; B (do nothing) leaves row 8 unchecked and the session stops on a check that cannot pass; C edits the register to move the key, which is a hand-edit of the SSOT and is refused. The defect is in the check's text slicing, not in the register: every criterion the row sets (resolved, verification, resolution_path naming Session 92, meu_links kept, the five keys, no add, the grouping line, LF) is still checked, by the row's own code. No M item is hit: no test assertion changes (M-7), no blocking gate is waived (M-11), since the same criteria are enforced, and a mechanical repair of a broken boundary under the existing rule is not new policy (M-3). Two-way: the failing receipt is kept beside the passing one for the reviewer."
open_decisions: []
```

Expert pass (fresh context): 3 briefs. Holds: none. Changed: D-1155, D-1156, D-1159. Not adopted: none.

Receipt: `C:/Temp/av-kit/mcp-audit-refresh/s92-expert-pass.txt`, with the coordinator's checks; adopted under HDP §5a step 6.

### D-1155: Does the `avkit_capture` description change need an MEU?

Expert pass: changed from "MEU-131 owns capture's action text": MEU-131 is the crop tool, so the reasoning now meets D-1132's product-cause test head on; A holds.

**I recommend A: no MEU; the change runs under its known issue in this session.** The grouping left this to the plan. Its rule asks for an MEU when the cause is in the product, and this one is, but you already made the product decision on this exact string (D-1134 A): what it says, its length and its acceptance check. The change adds no behaviour, and this session's tests, eval and review cover it. A new MEU would add a build-plan row and a status entry for that one string and decide nothing new.

- B: register a new MEU for the description and move its ACs into that MEU's family.
- Do nothing: the same as A; there is no MEU today.

Refs: grouping `:41`, §8 D-1132 (`:189`), D-1134; `meu-status.yaml:3433-3435`; `known-issues.yaml:5126`; M-8.

### D-1156: How should the census network proof sample?

Expert pass: changed from "a note after the exit-code list, and blocked meaning blocked with the signature": only the cancel check reads a signature, so blocked is now stated per check, and the note moves under the container run step; the any-versus-every reasoning holds.

**I recommend A: try each network check up to three times, about 5 seconds apart, and treat the network as blocked if any try is blocked (extract: any failure; cancel: the wall; compile: the retryable caption error).** Today one check that happens to get through counts a network failure as a product failure. Trying three times and counting any blocked try fixes that. The workflow gains one note under its container run step. The issue's own wording asks that every try be blocked, but that makes the false count more likely, not less, because each extra try is another chance for one to get through.

- B: three tries, and the network counts as blocked only if every try is blocked (the issue's words).
- C: keep one try and add only the note to the workflow.
- Do nothing: a container run on a flaky network can keep counting an environment failure as a product failure.

Refs: `known-issues.yaml:1191`; `run.ts:547-577`; M-3, M-6.

### D-1159: Which rows does the baseline update record?

Expert pass: changed from "handed to the agent": the earlier sessions' records say `--update-baseline` needs Mat's words, so this is M-4 and Mat's to rule; it went to Mat with A recommended.

**Mat ruled A on 2026-11-18: "A: record all five (Recommended)"** (AskUserQuestion in the coordinator session, relayed by the coordinator). The recommendation he ruled on: record all five actions that are waiting for the baseline (convert probe, and capture crop, frames, sheet and export). The audit writes every action the server offers, so it cannot record crop alone without a hand edit, which the workflow forbids. All five are already served, and each was approved, and put on this waiting list for this update, in its own earlier session. Nothing about any tool's shape changes; the baseline only catches up with what is served.

- B: record crop only. It needs a hand edit of the baseline and leaves the baseline test failing.
- C: skip the update this session. The crop issue stays open and the waiting list stays.
- Do nothing: the same as C.

Refs: `coverage.test.ts:15-22`; `known-issues.yaml:5021`; `run.ts:590-610`; `mcp-audit.md` exit criteria; grouping `:106`; the MEU-133 to MEU-136 handoffs; M-4, M-6.

### D-1161 and D-1162: what the executor does instead of stopping

Expert pass: inline, not independent.

These two used to stop the session for you. Under your 2026-11-18 words ("make the decisions always the recommenations"), each now has a recommended action that the executor takes and records in the handoff for you to read afterwards. Neither action edits the baseline by hand or changes the description beyond D-1134 A.

**D-1161, an audit that is not clean, or a baseline that fails its check: I recommend restoring and going on.** The baseline, report and coverage test go back to their row-0 bytes, the failing checks and deltas are recorded, each finding becomes an issue as the audit workflow asks, the baseline issue stays open, and the session finishes without the update. The committed baseline stays the last clean record, and a later session reruns the audit.

- B: stop and wait for you (the old reservation). It leaves the work unfinished for an action with one sensible answer.
- C: rerun until it passes. It can hide a real regression; refused.

**D-1162, an eval run that completes and fails: I recommend keeping the description and going on.** The description is your ruling, so a miss cannot change it here. The failing runs are recorded, a new issue holds the measured miss, and the description issue is still resolved because the model now sees the action text (AC-7 to AC-10).

- B: stop and wait for you (the old reservation).
- C: change the description to pass. Outside D-1134 A; refused.

Refs: grouping `:106`; `mcp-audit.md` step 5; `eval-run.md`; S7 to S9; M-8.

## Research References

- **Claude Code and tool descriptions:** Claude Code 2.1.325 cuts server instructions and upfront tool descriptions at 4,096 characters (code.claude.com/docs/en/mcp; grouping §8 D-1134), so a description under that limit reaches the model whole.
- **MCP `tools/list`:** a client sees each tool's `description` and `inputSchema`; `_meta` is for the client, and Claude Code does not show it to the model (D-1134's measurement, `C:/Temp/av-kit/triage-1117b/measure-desc.txt`, `first-lines.txt`).
- **Node `Atomics.wait`:** blocks the calling thread for a given time on a `SharedArrayBuffer` slot; allowed on Node's main thread, so `REAL_PROBES.sleep` needs no timer or `await`.

## Planning receipts

All under `C:/Temp/av-kit/mcp-audit-refresh/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `mar92-probe.py`, `mar92-probe.txt` | `HEAD` `ecfa3f3`, a clean tree, one worktree; line endings, sizes and SHA-256 prefixes of the scope; the new files and the handoff absent; the anchors with their lines; the three issues `open`, `YOUTUBE-CAPTIONS-IP-BLOCK` `resolved`; grouping rows 92 and 93; highest decision id in use D-1134; `decision_sources` on the grouping, the register, the issues and this plan |
| `mar-plan-desc-record.json` | The row-0 descriptions, `_meta` and input schemas of the eight tools, from the built server's `tools/list` |
| `mar-plan-desc-check-now.txt` | `desc-check.mjs --baseline … --expected …` at row 0: exit 1, 145 characters, "description is still the row-0 text" (the measured Red) |
| `mar92-trace-probe.py`, `mar92-trace-probe.txt` | `DESC_TRACE` on the expected file: 14 lines, 3,981 characters, no CR, the action heads in order, markers on lines 2 to 5 only, no sentence missing from its action's `_meta` |
| `mar-plan-eval-session64.txt` | `eval-rerun.py --session64`: Session 64's real result reproduced (t1 and t2 fail, t3 passes) |
| `mar-plan-desc-selftest.txt`, `mar-plan-eval-selftest.txt`, `mar-plan-baseline-selftest.txt` | The plan-time scripts' selftests, 0 failures each |
| `mar-plan-ruff-fmt-apply.txt` | `ruff format` on this folder's Python |
| `mar92-desc-candidate*` | The drafts of the expected description |
| `s92-expert-pass.txt` | The HDP §5a expert pass on D-1155, D-1156 and D-1159, with the coordinator's checks: all three changed, all adopted |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the three issues, grouping §3 Session 92 and §8 D-1132 to D-1134, the audit skill and workflow, and the code reads above | `mar-plan-2026-11-17-mcp-audit-refresh` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-1 to AC-15 | `mar-execution-2026-11-17-mcp-audit-refresh` |
