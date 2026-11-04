---
project: "2026-10-01-mcp-live-audit"
date: "2026-10-01"
source: "docs/build-plan/05-mcp-server.md#mcp-live-audit-residual"
meus: ["MEU-68"]
status: "approved"
template_version: "2.2"
---

# Implementation Plan: MCP live audit (Session 28)

> **Project:** `2026-10-01-mcp-live-audit`
> **Build plan:** `docs/build-plan/05-mcp-server.md` §MCP live audit (residual) (matrix row 5.3), plus §Destructive actions, §Testing (Phase 5) and §What this layer must not do
> **Grouping:** `.agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md`, Session 28 `mcp-live-audit`
> **Known issue:** `MCP-LIVE-AUDIT-WORKFLOW` (`.agent/context/known-issues.yaml:693`)
> **Reference protocol:** `_inspiration/_zorivest_mcp_tool_audit_skill.md` (the shape transfers; the domains do not)
> **Status:** `approved` by the independent plan review, Round 2 (user-directed Fable 5.1 subagent; `.agent/context/handoffs/2026-10-01-mcp-live-audit-plan-critical-review.md`). Execution waits for a direct human message ([human-gate-decision.md](human-gate-decision.md) §H-4); Part B also waits for `SEQUENCING_GATE`.

## Goal

`mcp-server/tests` stub HTTP with `vi.fn()` and call `handleTool` in-process (inventory: every file under `mcp-server/tests/` imports `handleTool` or `registerMcpSurface`; none spawns the server). Nothing drives the **built** MCP server as an IDE would, over stdio, against a running FastAPI with real state. A tool can therefore regress end to end (wrong route, stale schema, missing confirm handling, token/config drift, an action that returns 200 and produces nothing) while every suite stays green. That is the gap G25 records (`.agent/docs/emerging-standards.md:844`).

MEU-68 delivers:

1. A **runner** (`mcp-server/scripts/audit/`, `npm --prefix mcp-server run audit`). It spawns an isolated backend, launches `mcp-server/dist/index.js` over stdio with the env shape `copyMcpConfig` writes, calls all 67 actions of the 8 compound tools in dependency order, asserts **observable state** through an independent REST observer and the filesystem, refuses destructive calls without `confirm`, diffs a committed baseline, cleans up, and writes a report plus per-action receipts.
2. A **workflow** `.agent/workflows/mcp-audit.md` and a **skill** `.agent/skills/mcp-tool-audit/SKILL.md` that adapt the Zorivest phases to av-kit.
3. A committed **baseline** `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` and the **report** `.agent/context/MCP/mcp-tool-audit-report.md`, both from the first authoritative Windows run.
4. Spec-hub reconciliation: `05-mcp-server.md` §MCP live audit names actions that do not exist (D-5).

### Execution shape: build now, baseline later (Human-approved)

MEU-68 depends on MEU-18 (approved) and MEU-62 (`pending`, Session 27, not yet planned). The user chose on 2026-10-01 to **build now and baseline later** ([human-gate-decision.md](human-gate-decision.md) §H-3):

- **Part A (rows 1–8): runs as soon as execution is authorized.** It covers the runner, unit and fake-backend tests, the container subset run, the workflow, skill and docs, and the spec-hub reconciliation. No Part A row needs MEU-62 to *pass*. The container run still exercises the TTS surface: its MEU-62-attributable failures are tolerated only under `MEU62_PENDING_TOLERANCE`, which turns off once MEU-62 is approved (row 10 and the Windows gate tolerate none).
- **Part B (rows 9–12): waits for `SEQUENCING_GATE`.** It covers the merge of `main` carrying MEU-62, the authoritative Windows run, the committed baseline and report, and the known issues for findings. The independent execution review and closeout follow Part B, so the reviewer sees the baseline.

This is two active projects at once (Sessions 27 and 28), which departs from AGENTS §Session Discipline "One related project per session". The departure is user-directed and bounded by `PART_A_PATHS` (below): Part A writes no product tree Session 27 owns (`packages/`, `ui/`, `mcp-server/src/`). Both sessions do write the shared SSOT files; `SSOT_MERGE_RULE` resolves that at the row-9 merge.

---

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json absent (ls: No such file or directory, 2026-10-01); `pip show headroom` → not found. Scope is TypeScript MCP runner + workflow docs, routed to direct file/search by .agent/docs/context-tool-decision-gate.md."
  human_message_reference: null
```

Re-evaluated before execution in task row 1.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the claude.ai/code container (Linux, `bash`, no `rtk`, no `pwsh`, no Codex CLI, no display). Per `.agent/docs/harness-profiles.md` §Notes "Claude Code in the claude.ai/code cloud container" and `.agent/context/harness.local.md` §Claude Code: `plan_to_exec_gate: human`, `native_shell: bash`, `fresh_worker: Agent tool + .claude/agents/`, `can_dispatch_external_reviewer: no` in practice. The Cursor `reviewer-auto` override does **not** apply. Reviewer `approved` does not start execution; a direct user message does.
- **Shell and receipts:** container rows use POSIX form `> "${RECEIPTS_DIR}/s28-<id>.txt" 2>&1; code=$?; …; exit $code` with `RECEIPTS_DIR` exported (a scratchpad `receipts/` directory; row 1 records it). Windows rows use `rtk proxy … *> C:/Temp/av-kit/s28-<id>.txt`.
- **RTK:** absent in the container (`which rtk` → nothing, 2026-10-01). Container rows invoke tools raw, which is the unfiltered equivalent of `rtk proxy`. This is the Session 26 amendment A2 precedent (`docs/execution/plans/2026-09-28-p11-capture-settings/task.md` §Task Table, "Container runs"), recorded as D-11. The Windows script uses `rtk proxy`.
- **Reviewer (USER_EXPLICIT, same-vendor exception):** Fable 5.1 subagent for plan and execution review; see [human-review-decision.md](human-review-decision.md). Author and reviewer are both Anthropic models. The deviation from PROFILE B1/B4 is disclosed, not hidden. The author dispatches and corrects; it never writes a verdict.
- **Cloud/local split:** applies per `.agent/docs/cloud-local-collaboration.md` §1, because the authoritative run needs the Windows target (real Kokoro, ffmpeg, `mss` capture). The gate location and the execution authorization are recorded in [human-gate-decision.md](human-gate-decision.md).

## Handoff Set

| Scope | Canonical path |
|---|---|
| MEU-68 | `.agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md` |
| Plan review | `.agent/context/handoffs/2026-10-01-mcp-live-audit-plan-critical-review.md` (rolling, cap 3) |
| Project review | `.agent/context/handoffs/2026-10-01-mcp-live-audit-implementation-critical-review.md` (rolling, cap 6) |

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Prerequisites, decisions, pre-edit MCP baseline, hypothesis known issue (row 1) | — | `shared` | `walkthrough.md` §Prerequisites; `s28-prereq.txt` |
| WP-2 | Tests first (Red), then pure modules, then runner orchestration (Green) (rows 2–4) | WP-1 | `compact_continue` | Test files; runner modules; Red/Green receipts; re-read `task.md` + `walkthrough.md` after compaction |
| WP-3 | Typecheck coverage, scripts, D6 registration, container subset run (rows 5–6) | WP-2 | `shared` | `s28-audit-container/`; walkthrough §Container run |
| WP-4 | Workflow, skill, READMEs, spec-hub reconciliation, Part A targeted gate, Part A checkpoint (rows 7–8) | WP-3 | `compact_continue` | Docs; `s28-gate-a.txt`; walkthrough §Part A checkpoint; pushed SHA |
| WP-5 | Part B: `SEQUENCING_GATE`, merge, container pregate, `WINDOWS_GATE`, baseline/report, findings (rows 9–12) | WP-4 | `compact_continue` | `windows-gate-result.json`; baseline; report; known issues |
| WP-6 | H1 closeout, independent execution review, H2 | WP-5 | `shared` | Handoff; rolling review; reflection; metrics |

Every `compact_continue` row resumes by re-reading `task.md`, `walkthrough.md` and the latest receipt named in its row.

---

## User Review Required

> [!IMPORTANT]
> Recorded decisions (2026-10-01; H-1 in [human-review-decision.md](human-review-decision.md), H-2 and H-3 in [human-gate-decision.md](human-gate-decision.md)):
> - **H-1** reviewer: Fable 5.1 subagent.
> - **H-2** audit target: an isolated spawned backend, never the user's running app.
> - **H-3** sequencing: build now, baseline later.
>
> Still open, for the execution message (§Decision Log, Decision Brief H-4): the execution authorization and the gate location. **Recommendation:** split like Sessions 25 and 26. Part A runs in this container; Mat runs one Windows `WINDOWS_GATE` (`validate-task.ps1 -Check windows-gate`) in Part B. A plain "proceed" is read as accepting H-4's recommendation and every autonomous decision below. It also authorizes commits and pushes to `claude/sweet-goodall-mu69td` and merging `origin/main` into it at row 9. It authorizes no PR, merge to `main`, release or deploy.
>
> Two scope notes for the reader:
> - **"Execute each MCP call in IDE".** The user's words in `MCP-LIVE-AUDIT-WORKFLOW` are delivered by a scripted stdio MCP client, the same transport and env an IDE uses (spec §Client row, Research-backed). It is not an IDE agent calling tools by hand. The workflow also documents a short manual IDE spot-check (AC-68.16), but that check is not the authority.
> - **A probable shipping defect was found during planning; it is not fixed here (D-6).** The installed IDE config (`docs/distribution/mcp.json.example`) runs `${RESOURCES}/mcp-server/index.js`. The entry guard (`mcp-server/src/index.ts:31-34`) starts the server only for paths ending `/dist/index.js` or `/src/index.ts`. Also, `ui/electron-builder.yml` copies `../mcp-server/dist` with no `node_modules`. Both point to an installed MCP server that never serves. Row 1 files it as a hypothesis known issue. The Windows request adds an optional, non-blocking packaged probe to confirm it on the target.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once here and referenced by name everywhere else (create-plan §Single-statement rule).

| Name | Definition |
|---|---|
| `AUDIT_ACTION_SET` | The closed set of `(tool, action)` pairs in `ACTION_INDEX`, `mcp-server/src/toolsets/registry.ts:51-119`: 67 rows over the 8 `COMPOUND_TOOLS` at planning (`registry.ts:22-31`; download 18, transcript 12, tts 5, models 7, settings 2, health 2, convert 13, capture 8). It is **68 since the row-9 merge of MEU-62**, which appended `avkit_models.download_asset` (A7). The runner and tests derive the set from `ACTION_INDEX`; the gate scripts state the count once as `AUDIT_ACTION_COUNT`. |
| `DESTRUCTIVE_SET` | `DESTRUCTIVE_ACTIONS`, `mcp-server/src/destructive.ts:1-9`: download.remove, download.clear, transcript.remove, tts.cancel, convert.remove, convert.clear, capture.remove. |
| `MCP_LAUNCH` | `command: node`, `args: [<server path>]`. Default server path is `mcp-server/dist/index.js`. Env is exactly `{AVKIT_API_TOKEN, AVKIT_APP_DATA}` (the `copyMcpConfig` payload, `ui/src/main/ipc.ts:392-405`), plus the OS keys a child process needs to start: `PATH`, `SystemRoot`, `TEMP`, `TMP`, `HOME`/`USERPROFILE`. `AVKIT_API_BASE` is never set, so the server discovers the API through `{AVKIT_APP_DATA}/backend.json` (`mcp-server/src/config.ts:140-153`), as the default Copy MCP config does. |
| `ISOLATED_ROOT` | A fresh temp directory per run (`os.tmpdir()/avkit-mcp-audit-<timestamp>-<rand>`). It contains `app-data/` (passed as `--app-data` to the spawned backend and as `AVKIT_APP_DATA` to the server) and `out/{downloads,transcripts,tts,convert,captures,models}`. |
| `ISOLATION_GUARD` | Before the first mutating step, the runner sets every output-path setting the backend uses under `ISOLATED_ROOT/out/` through `avkit_settings.set`, re-reads them through the REST observer, and refuses to continue (exit 3, zero mutating calls made) if any resolved path is outside `ISOLATED_ROOT`. The key set is `ISOLATION_KEYS`, derived **structurally** from the `avkit://settings/schema` resource: every string key named `path`, `*_path`, `*_dir` or `*_directory`. Today that is `downloader.path`, `transcript.output_dir`, `tts.models_directory`, `tts.output_path`, `converter.output_dir` and `capture.inbox_dir` (`mcp-server/src/toolsets/settings.ts:16,29,40,44,58,64`). `tts.output_path` defaults to `~/Documents` and is where `services/tts.py:194` writes. `downloader.ffmpeg_path` and `downloader.cookie_file_path` are inputs, not outputs: they are left at their defaults and never written to. A new path-like key in the schema that has no mapping makes the guard fail closed. |
| `REST_OBSERVER` | An independent `fetch` client in the runner that reads `http://127.0.0.1:<port>/api/v1` with the **GUI** token it passed as `--token`. It never goes through the MCP server, so the MCP result and the observed state come from two different paths. |
| `OBSERVABLE_RULE` | A step's verdict is `pass` only if its MCP call returned the expected `isError` **and** its declared observable (a `REST_OBSERVER` read or a filesystem check, named per step in `AUDIT_PLAN`) holds. An MCP success whose observable does not hold is `fail` with reason `hollow` (G25). The MCP envelope alone never passes a step. Each step record's `error` field holds the first that applies: the MCP text when `isError` is true; otherwise the entity's `error_message` when the observable reads a terminal failed state (for example the TTS job row); otherwise the observable's detail. Dependents of a failed step (for example `tts.get` and `tts.cancel` after `tts.generate`) are `blocked` with `blocked_by`. |
| `REFUSAL_ORACLE` | For each member of `DESTRUCTIVE_SET`, two refusal calls are made on a live fixture: one with `confirm` omitted, one with `confirm: false`. Each must return `isError: true` and leave the step's observable unchanged (same row/status/file read before and after). Only then is the `confirm: true` call made, and it must change the observable. An `isError: true` refusal whose observable changed is `fail` (`refusal_mutated`). A refusal that returns `isError: false` is `fail` (`refusal_missing`). The refusal text may be the handler's `validation_error:`, `confirm_required:`, or the SDK's `Input validation error` (D-4). |
| `AUDIT_PLAN` | The ordered step list in `mcp-server/scripts/audit/plan.ts`: Phase 2 lifecycles and Phase 3 functional steps (table below). Every member of `AUDIT_ACTION_SET` appears in at least one step. |
| `VERDICT` | Closed enum `pass \| fail \| skip_env \| blocked`. `blocked` means a step did not run because an earlier step it depends on did not pass. |
| `DELTA` | Closed enum `REGRESSION \| KNOWN \| FIXED \| NEW \| REMOVED \| UNCHANGED`. Rules: baseline pass → now non-pass = `REGRESSION`; baseline fail → now non-pass = `KNOWN` (carrying the baseline's `issue` id); baseline fail → now pass = `FIXED`; not in baseline = `NEW`; in baseline but not served by `tools/list` = `REMOVED`, counted as a regression; baseline pass → pass = `UNCHANGED`. |
| `ENV_BOUND_AUDIT` | **Container mode only.** The `(tool, action)` pairs that may be `skip_env` in the container, each with a signature regex over the decisive error text **and** an environment proof. The planning-time candidates are listed under §Environment-bound census. Members are added only with a row-6 proof (`cloud-local-collaboration.md` §4). Authoritative mode tolerates none. |
| `MEU62_PENDING_TOLERANCE` | **Container mode, Part A only.** While `uv run python tools/meu_status.py get MEU-62` reports a status other than `approved`, `validate-task.sh audit-container` tolerates a `fail` on `tts.generate`, `tts.get`, `tts.cancel` and `models.load`. This applies only when the decisive error matches `MEU62_SIGNATURE` (`en_core_web_sm\|spacy\|vocab\|config\.json\|misaki`, case-insensitive; the `TTS-GENERATE-FAILED-SILENT` causes, `known-issues.yaml:126-127`). The **runner** still reports these as `fail` and exits 1; the tolerance lives in the validation script, never in the runner. Once MEU-62 is `approved` the tolerance is off (rows 10, 11). Row 6 records the actual matched text. |
| `TEST_SETS` | `UNIT_TESTS` = `mcp-server/tests/audit/{classify,coverage,baseline,isolation,ledger,report,redact}.test.ts` (pure modules, row 3). `RUNNER_TESTS` = `tests/audit/{run-cli,runner-fake-backend}.test.ts` (row 4). `DOC_TESTS` = `tests/audit/docs.test.ts` (row 7). Row 2's Red runs all three sets. `green` runs `UNIT_TESTS`; `fake` runs `UNIT_TESTS` + `RUNNER_TESTS`; `docs` runs `DOC_TESTS`; `gate-a` and later run the whole MCP suite. `VITEST_ACS` = AC-68.1–68.14 and AC-68.16. AC-68.15, 68.17 and 68.18 are proven by the Windows gate, the typecheck receipts and `docs` respectively, not by Vitest titles. Doc-tests assert file existence with `expect(existsSync(...))` before reading, so their Red is an assertion, not an `ENOENT` throw. |
| `SSOT_MERGE_RULE` | At the row-9 merge of `origin/main`, conflicts in tool-managed SSOT (`meu-status.yaml`, `meu-registry.md`, `known-issues.yaml`/`.md`, the `AUTOGEN` regions of `BUILD_PLAN.md`) are resolved by taking `origin/main`'s version, then re-applying Session 28's own changes through the tools: `meu_status.py update MEU-68 …`, `issue_triage.py add` for `MCP-PACKAGED-ENTRY-UNREACHABLE`, then `render`. Generated regions are never hand-merged. Prose files (`current-focus.md`, `.agent/docs/commands.md`) are merged by hand, keeping both sessions' lines. `seqgate` then requires `meu_status.py render --check` and `issue_triage.py render --check` to pass. |
| `STALE_SPEC_PATTERNS` | The literals that must not remain in 05 §MCP live audit after AC-68.18: `status→pause`, `get→set→reset`, `health.liveness/dependencies/gpu`, `GUI action index`. `validate-task.sh docs` greps exactly these (fixed strings). |
| `CLEANUP_PREDICATE` | At the end of the run all of these hold: the `REST_OBSERVER` reports zero downloads, transcripts, conversions, captures and pending capture requests; every settings namespace equals the snapshot taken right after `ISOLATION_GUARD`; the spawned backend process has exited; and, unless `--keep`, `ISOLATED_ROOT` is removed. Any residual is listed as a finding, `cleanup_ok: false`, exit 1. |
| `BASELINE_UPDATE_RULE` | `--update-baseline` writes `baseline-snapshot.json` only when `--mode authoritative`, `process.platform === "win32"`, `cleanup_ok`, and zero `REGRESSION`/`REMOVED`. Otherwise the runner exits 2 and leaves the file byte-identical. A missing baseline file is an error (exit 4) unless the run passes `--no-baseline` (every pair is then `NEW`), which is how Part A's container run and the first authoritative run start. With `--no-baseline`, `--baseline <path>` names only the file `--update-baseline` writes; nothing is read from it. |
| `BASELINE_ANNOTATION_RULE` | After the authoritative run, the cloud may change the committed baseline **only** by setting `issue` on non-`pass` entries to ids that exist in `known-issues.yaml` (row 12). The entry set, every `status` and `recorded_commit` must stay byte-equal to the gate-produced copy (`windows-gate-baseline.json` in this plan folder). `validate-task.sh findings-check` enforces this, so the annotation does not reopen the gate. |
| `AUTHORITATIVE_ACCEPTANCE` | The authoritative run counts for MEU-68 when all of these hold: it ran to completion with no runner error; `cleanup_ok`; health.liveness, health.dependencies and tts.generate are `pass` (grouping D-4: the first baseline must record a working `tts.generate`); and every other non-`pass` has a known issue filed through `tools/issue_triage.py` and recorded as `issue` on its baseline entry. Finding defects is the audit's job: a filed `fail` does not fail MEU-68. A `fail` with no filed issue does. |
| `SEQUENCING_GATE` | The JSON printed by `uv run python tools/meu_status.py get MEU-62` (`tools/meu_status.py:98-108`) parses with `.status == "approved"` on the merged tree; `git merge-base --is-ancestor origin/main HEAD` holds after the row-9 merge; and both render checks of `SSOT_MERGE_RULE` pass. The status is read by JSON parse, never by text grep. |
| `PART_A_PATHS` | Part A (rows 1–8) may write only `mcp-server/scripts/**`, `mcp-server/tests/audit/**`, `mcp-server/package.json` (scripts block only), `mcp-server/tsconfig.scripts.json`, `.agent/workflows/mcp-audit.md`, `.agent/workflows/README.md`, `.agent/skills/mcp-tool-audit/**`, `.agent/skills/README.md`, `.agent/docs/commands.md`, `docs/build-plan/05-mcp-server.md`, `docs/BUILD_PLAN.md`, this plan folder, this project's handoffs/reviews (`.agent/context/handoffs/2026-10-01-mcp-live-audit-*`, A6), and tool-rendered SSOT (`.agent/context/meu-status.yaml`, `meu-registry.md`, `known-issues.yaml`/`.md`, `current-focus.md`). `mcp-server/package-lock.json`, `mcp-server/src/**`, `packages/**`, `ui/**` must be unchanged. Checked by `validate-task.sh scope`. |
| `GATED_PATHS` | Everything the Windows gate executes or reads: `mcp-server packages pyproject.toml uv.lock docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.ps1`. Any later commit touching them reopens the gate (`cloud-local-collaboration.md` §3.4). The baseline is not in this set: the first run uses `--no-baseline`, and later edits are bounded by `BASELINE_ANNOTATION_RULE`. |
| `AUDIT_FIXTURES` | Defined once in `mcp-server/scripts/audit/fixtures.ts`; all values can be overridden by CLI flag (D-7). `download_url_a = https://www.youtube.com/watch?v=jNQXAC9IVRw` (19 s), `download_url_b = https://www.youtube.com/watch?v=dQw4w9WgXcQ` (the backend's own `SABR_PROBE_URL`, `youtube/adapter.py:82`), `transcript_channel_url = https://www.youtube.com/@jawed` (a one-video channel), `tts_text` (a short fixed English sentence; A8 removed `tts_long_text`), a 2 s `lavfi testsrc` MP4 the runner generates with the ffmpeg path `avkit_health.dependencies` reports, and a 64×64 PNG the runner writes for the container capture seed. |

### Runner design (resolved by D-1, D-2, D-3, D-8)

| File (`mcp-server/scripts/audit/`) | Responsibility |
|---|---|
| `run.ts` | CLI: `--mode container\|authoritative` (required), `--out <dir>`, `--baseline <path>`, `--update-baseline`, `--no-baseline`, `--report <path>`, `--server <path>`, `--discovery-only`, `--keep`, `--agent <name>`, fixture overrides. Paths are absolute: `npm --prefix` runs the script with cwd `mcp-server/`. Runs Phase 1 → 5 and sets the exit code: 0 pass, 1 audit failure or residual, 2 baseline rule refused, 3 isolation refused, 4 runner/launch error. |
| `backend.ts` | Creates `ISOLATED_ROOT`. Spawns `uv run python -m avkit_api --token <gui> --mcp-token <mcp> --port 0 --app-data <ISOLATED_ROOT/app-data>`, the same argv Electron uses (`ui/src/main/python-manager.ts:16-35`). Runs `uv` with cwd = the repo root, resolved from the script's own location, because `npm --prefix` starts it in `mcp-server/`. Writes `mcp-token.txt` and waits for `AVKIT_READY port=` (pattern from `tests/integration/test_backend_spawn.py:29-64`). Owns the `--mcp-token` value and tears down: process exit, then root removal. |
| `client.ts` | SDK `Client` + `StdioClientTransport` with `MCP_LAUNCH` (SDK `^1.30.0`, already a dependency). Captures server stderr into the receipts with tokens redacted. |
| `observer.ts` | `REST_OBSERVER`. |
| `plan.ts` | `AUDIT_PLAN`: steps `{id, tool, action, args, depends_on, observable(ctx) → {ok, detail}, destructive?}`. |
| `discovery.ts` | Phase 1: `tools/list` → tool names + per-tool action literals read from each tool's `inputSchema` (the `action` const of each union branch) and `_meta.action_descriptions` keys. Both must agree. |
| `classify.ts` | Pure: verdict computation, `DELTA`, `ENV_BOUND_AUDIT` matching, coverage, summary counts, and the `ISOLATION_GUARD` predicate over a settings read-back (`ISOLATION_KEYS` derivation from the schema included), which `isolation.test.ts` covers in row 3. Exhaustive `switch` over `VERDICT` and `DELTA` with a `never` default. |
| `ledger.ts` | Cleanup ledger: every created job/shot/request/file registered at creation; `CLEANUP_PREDICATE` evaluation. |
| `report.ts` | Writes `actions.jsonl` (one record per call), `mcp-audit-summary.json` (schema `mcp-audit-summary.v1`, `mcp-server/scripts/audit/summary.schema.json`, whose `steps[].tool` is an enum of the 8 `COMPOUND_TOOLS`), and the Markdown report. |
| `redact.ts` | Removes every token value (GUI, MCP) from any string written to disk. |
| `fixtures.ts` | `AUDIT_FIXTURES`. |

The runner runs through `tsx` (an existing devDependency) and **never imports `src/toolsets` or `dist/toolsets`** (spec §Client). It talks to the server only over stdio.

### `AUDIT_PLAN`: lifecycles and observables

Spec §Phase 2/3 names, reconciled to the real actions (D-5). "Parity" means the MCP payload's ids and counts equal the `REST_OBSERVER` read (G25: data presence and equivalence, not status codes). Each domain runs in this order, after Phase 1 and `ISOLATION_GUARD`.

| Domain | Steps in order (refusals per `REFUSAL_ORACLE` marked †) | Observable per step |
|---|---|---|
| settings | `get` each namespace → `set` one reversible key per namespace → `get` → `set` original back | REST `GET /settings/{ns}` equals the MCP payload; after `set`, the REST value equals the new value; after the restore, it equals the snapshot |
| health | `liveness` → `dependencies` | REST `GET /health` 200 with the same version; `dependencies` lists ffmpeg and yt-dlp, matching REST (authoritative: both `found`) |
| models | `available` → `download` (smallest ONNX variant) → poll `download_runtime` until done → `downloaded` → `load` → `status` → (tts domain) → `unload` → `status` | REST `/models/download-runtime` reaches done; the variant appears in REST `/models/downloaded` and its files exist under `out/models`; REST `/models/status` shows it loaded, then unloaded |
| tts | `voices` → `prepare` → `generate` (`tts_text`) → poll `get` until terminal → `generate` (second job, `tts_long_text`) → precondition: REST shows job 2 non-terminal → `cancel`† | REST voices equal MCP; `prepare` returns non-empty prepared text and creates no job (REST `GET /tts/{returned-id}` absent, if an id is returned); job 1 reaches done per REST `GET /tts/{id}` and its output file exists under `out/tts` with size > 0 and a RIFF/ID3/MP3 frame header; after `cancel`, job 2's REST status is cancelled; the refusals leave it unchanged. Cancel on a finished job is a 204 no-op (`services/tts.py`), so `tts_long_text` (about 3,000 characters) keeps job 2 running. If the precondition read shows job 2 already terminal, the step is re-established once with a fresh job and recorded `precondition_reestablished`; a second loss is `fail` |
| download | `apply_defaults` → `add` url_a → `add` url_b → `list` → `get` → `reorder` (swap) → `pause` → `resume` → `start` → poll `get` url_a until terminal → `cancel` (queue-level, no `id`; it acts on the active job, url_b) → `reset` url_b → `stop` → `sabr_get` → `sabr_force` → `sabr_check` → `sabr_clear` → `cookies_test` (`mode: none`) → `remove`† url_a → `clear`† | REST rows exist with Queued status; `list` parity; REST order equals the swap; REST processor paused/running/idle; url_a Completed and the media file exists under `out/downloads` with size > 0; url_b Cancelled then Queued (the observable of the queue-level `cancel` is pinned at row 3 from `services/download.py:278` `cancel_processing`); REST `/downloads/sabr` reflects force/clear; `cookies_test` ok; url_a is REST 404 after `remove`; REST list is empty after `clear`; the refusals leave both unchanged |
| transcript | `add` channel → `list` → `get` → `reorder` ([id]) → `start` → `pause` → `resume` → poll until ≥ 1 item is terminal → `stop` → `compile` → `requeue` / `retry` from legal states (below) → `remove`† | REST job row with `video_count ≥ 1`; `list` parity; processor states; an item terminal per REST; the compile output file exists under `out/transcripts`. `requeue` and `retry` are each called once from a state where `TRANSCRIPT_PARENT_TRANSITIONS` (`domain/transcript.py:24-37`) allows `→ Pending`, which means Processing, Cancelled or Failed, never Pending or Done; REST then shows Pending. Each is also called once on a Done job, which must give `isError` with the 409 conflict envelope and leave the REST status Done (05 §Testing "ErrorEnvelope 422/409"). Row 3 pins the MCP-reachable sequence that yields a legal state, from `services/transcript.py` `stop_processing`/`requeue_channel`/`retry_failed_channel`. With the one-video `@jawed` fixture, "≥ 1 item terminal" usually means the job is Done. The candidate sequence therefore reaches Cancelled through `start` → immediate `pause` (Processing → Paused) → `stop`, if `stop` takes Paused → Cancelled (to be confirmed at row 3), then `requeue`. It repeats `start` → `pause` → `stop` before `retry`. The `tts.cancel` precondition-read rule applies: re-establish once, then `fail`. If none is reachable through MCP actions, that is a Stop Condition, not a weaker assertion. REST 404 after `remove` |
| convert | `add` (generated MP4) → `add` (second) → `list` → `get` → `reorder` → `pause` → `resume` → `start` → poll until job 1 is terminal → `cancel` (queue-level, no `id`; acts on the active job 2) → `reset` job 2 → `gpu` → `gpu_refresh` → `remove`† job 1 → `clear`† | REST rows; parity; order; processor; job 1 Completed and the output exists under `out/convert` with size > 0; job 2 Cancelled then Queued; `gpu` equals REST `/conversions/gpu`; `gpu_refresh` returns a probe whose REST read matches; REST 404 / empty; the refusals leave both unchanged |
| capture | `capture` (authoritative: `mode: fullscreen`; container: shot seeded through REST register mode, D-8) → `list` → `get` → `image` → `annotate` → `get` → `capture_interactive` → `list_requests` → (REST cancel of the request, cleanup) → `remove`† | REST shot row and PNG file under `out/captures`; `list` parity; `image` bytes equal REST `GET /captures/{id}/image` bytes and start with the PNG signature; after `annotate`, the REST detail carries the annotations; the pending request appears in REST `/captures/requests`; REST 404 after `remove`, file state per `09-screenshot-capture.md`; the refusal leaves the row |

Phase 3 (functional; spec names reconciled, D-5): `health.liveness`, `health.dependencies`, `download.cookies_test`, `download.sabr_get/sabr_check/sabr_force/sabr_clear`, `convert.gpu/gpu_refresh` and `models.download_runtime`. These sit in the lifecycles above, and the report tabulates them as status, the error code if any, and notes. These behaviors are pinned at row 3 from code and recorded in `walkthrough.md`, each with its file:line: the observable for `download.apply_defaults`, the file state after `capture.remove`, the observables of the queue-level `download.cancel` and `convert.cancel`, and the transcript legal-state sequence.

### Environment-bound census (container mode only)

Candidates, each with a planning-time code citation. A candidate becomes a member only when row 6 records the decisive error and the environment proof (`cloud-local-collaboration.md` §4). Steps that depend on a skipped step are `blocked` and inherit its member status.

| Candidate | Why the container cannot run it | Signature (regex over the decisive error) | Environment proof |
|---|---|---|---|
| `capture.capture` | `_require_windows()`, `avkit_infra/capture/adapter.py:113,118,159-161` | `screen capture requires Windows` | `process.platform !== "win32"` |
| `download.add`, `download.start`, `download.sabr_check`, `transcript.add`, `transcript.start` | network yt-dlp extract/probe through the proxy | fixed at row 6 from the real error text | the same URL fails from `uv run python -c` with yt-dlp outside the runner |
| `models.download` (and the `models.load`, `tts.generate` dependents) | Hugging Face download through the proxy and model size | fixed at row 6 | `hf_hub_download` fails outside the runner, or the disk allowance is proven exhausted |
| `convert.start`, `convert.gpu`, `convert.gpu_refresh`, `tts.generate` MP3 encode (and the generated MP4 fixture) | ffmpeg may be absent | `ffmpeg` not found | `avkit_health.dependencies` reports ffmpeg not found |

Anything else non-`pass` in the container is a real failure (fail closed). `AUTHORITATIVE_ACCEPTANCE` never consults this census.

### MEU-68 — `mcp-live-audit`

#### Boundary Inventory

The runner adds no new product input surface. Its external inputs are its CLI flags, its fixture overrides, the baseline file it reads, and the MCP/REST responses it parses. Product boundaries are exercised, not changed.

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input behavior |
|---|---|---|---|---|
| Runner CLI flags | `run.ts` parser (`node:util` `parseArgs`, `strict: true`) | `--mode` ∈ {container, authoritative} required; paths must resolve; `--update-baseline` only per `BASELINE_UPDATE_RULE` | unknown flag → exit 4 with a usage message, before any spawn | exit 4, no backend spawned (AC-68.12) |
| `baseline-snapshot.json` | `scripts/audit/baseline.schema.json` (schema `mcp-audit-baseline.v1`), validated with a hand-written validator in `classify.ts`, no new dependency | `schema` const; `recorded_commit` 40-hex; `mode` const `authoritative`; `entries[]` `{tool, action, status ∈ VERDICT, issue?}`; no duplicates | extra keys → reject | exit 4 naming the field; never treated as an empty baseline (AC-68.10) |
| MCP `tools/list` / `tools/call` results | SDK result types | `isError` boolean; `content[]` text/image | unknown shape → step `fail` (`malformed_result`) | fail closed (AC-68.12) |
| REST observer responses | the av-kit API (`openapi.committed.json`) | status codes per route | not parsed beyond the fields the observable names | non-2xx where 2xx expected → observable false |
| Product destructive input | MCP Zod `confirm: z.literal(true)` (`download.ts:86-87` and peers) | — | `.strict()` (existing) | exercised by `REFUSAL_ORACLE` (AC-68.7) |

#### Acceptance Criteria

Type per control C3. Every control AC names its observable, call chain and negative oracle (create-plan §Control-binding).

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-68.1 | integration | **Launch as an IDE does.** The runner launches the server per `MCP_LAUNCH` and completes `initialize`. Only the env keys named in `MCP_LAUNCH` reach the child process. The server finds the API through `backend.json` in the isolated app-data. Observable: `summary.launch = {command, args, env_keys, initialized}`. Chain: `run.ts main → client.ts connect → StdioClientTransport spawn → dist/index.js main()`. | Spec §Client; Local Canon `ipc.ts:392-405`, `config.ts:140-178` | Fake-backend test launches with `AVKIT_API_TOKEN` omitted: the first tool call returns `token_missing`, `summary.launch.initialized` stays true, discovery is `fail` and the exit code is 1. A test asserts the child env keys equal the allowed set exactly. |
| AC-68.2 | unit | **No in-process shortcut.** No file under `mcp-server/scripts/` imports `src/toolsets`, `dist/toolsets`, `handleTool` or `registerMcpSurface`. | Spec §Client | `validate-task.sh scope` runs `rg` over `scripts/` for those four names; the test seeds a temp file with one of them and asserts the check fails. |
| AC-68.3 | unit | **Discovery classification.** Given served `(tool, action)` pairs and a baseline, `classify.discovery()` returns `NEW` for served-not-baselined, `REMOVED` for baselined-not-served, and `GHOST` for served actions whose call returned an unknown-action error. A disagreement between `inputSchema` literals and `_meta.action_descriptions` keys is a discovery `fail`. | Zorivest §Phase 1; Local Canon `registry.ts` | Three fixtures, one per outcome, plus a schema/meta mismatch fixture. |
| AC-68.4 | integration | **Discovery against the built server** yields exactly the 8 `COMPOUND_TOOLS` and the pairs of `AUDIT_ACTION_SET`. Observable: `summary.discovery.{tools,actions}`. Chain: `run.ts → discovery.ts → client.listTools()`. | Spec §Phase 1 | A fake-server test that serves a 9th tool name gives a discovery `fail` naming it. |
| AC-68.5 | unit | **Coverage.** Every pair in `AUDIT_ACTION_SET` (imported from `src/toolsets/registry.ts` **in the test only**) appears in at least one `AUDIT_PLAN` step, and the committed baseline's entries equal `AUDIT_ACTION_SET` once it exists (Part B). | Spec "executes every compound-tool action" (`meu-registry.md:66`) | `coverage()` called on a copy of the plan with one step removed returns that pair as missing. |
| AC-68.6 | integration | **`OBSERVABLE_RULE`.** Every `pass` record in `actions.jsonl` carries a non-null `observable` detail. A step whose MCP call succeeds while the observable fails is `fail` with reason `hollow`. Chain: `run.ts → plan step → client.callTool → observer.ts / fs → classify.verdict`. | G25 (`emerging-standards.md:844`); Spec §Phase 2 | The fake backend returns 201 for `POST /downloads` but 404 for `GET /downloads/{id}`: `download.add` is `fail`/`hollow`, the exit code is 1, and the report issues log lists it. |
| AC-68.7 | integration | **`REFUSAL_ORACLE`** holds for all 7 members of `DESTRUCTIVE_SET`. Observable: per-member records `{refusal_omit, refusal_false, confirmed}` in `actions.jsonl`. Chain: `plan.ts destructive step → client.callTool ×3 → observer before/after`. | Spec §Destructive; Local Canon `destructive.ts`; Research-backed D-4 | Unit: `verdict.refusal()` returns `fail`/`refusal_mutated` when the observable changed under `isError: true`, and `fail`/`refusal_missing` when `isError: false`. Fake-backend: a `DELETE` request received during a refusal call makes the step `fail`. |
| AC-68.8 | integration | **Isolation (H-2).** The backend runs on `ISOLATED_ROOT/app-data`; `MCP_LAUNCH.env.AVKIT_APP_DATA` equals it; `ISOLATION_GUARD` passes before any mutating call. Observable: `summary.isolation = {root, paths{}, ok}`. Chain: `run.ts → backend.ts spawn → settings set → observer re-read → guard`. | Human-approved H-2; Local Canon `settings.ts` defaults | Unit: a settings read-back with one path outside the root makes the guard throw; a schema fixture with an extra unmapped `*_dir` key makes it throw. A fake-backend test asserts exit 3 and zero mutating requests recorded by the fake. A test asserts the runner never reads `%LOCALAPPDATA%/av-kit` or `~/.avkit` (the env passed to the child process names only the isolated root). |
| AC-68.9 | integration | **`CLEANUP_PREDICATE`.** Observable: `summary.cleanup = {ok, residuals[], backend_exited, root_removed}`. Chain: `ledger.ts register at create → run.ts finally → observer counts → process wait → rm`. | Zorivest §Cleanup Contract; Spec §Cleanup | Unit: a ledger with one unremoved job gives `ok: false` with the residual named, and the exit code is 1. Container run (row 6): `cleanup.ok` true and the root absent afterwards. |
| AC-68.10 | unit | **`DELTA` classification and baseline schema.** All six `DELTA` outcomes are computed per the rule. A malformed baseline (bad schema id, duplicate entry, extra key, non-40-hex commit) is rejected with exit 4 and never treated as empty. | Zorivest §Phase 4; Spec §Phase 4 | One fixture per `DELTA` value; four malformed-baseline fixtures. Exhaustiveness: the TS `never` default makes adding an enum member a compile error, which the typecheck covers through AC-68.17. |
| AC-68.11 | unit | **`BASELINE_UPDATE_RULE`.** | Spec §Phase 4 "baseline updated"; Local Canon cloud-local §2 (authority is local) | `--update-baseline` with `--mode container` → exit 2 and the baseline file's SHA-256 unchanged; authoritative mode with one `REGRESSION` → exit 2 and unchanged; authoritative on a non-win32 platform → exit 2. |
| AC-68.12 | unit | **Fail-closed tolerance.** Container mode accepts `skip_env` only for an `ENV_BOUND_AUDIT` member whose signature **and** environment proof both match, and `blocked` only beneath such a member. Authoritative mode treats every non-`pass` as counted. An unknown CLI flag, a malformed MCP result or an unclassified exception is a failure, never a skip. | Local Canon cloud-local §4 | A member with non-matching text → `fail`; a non-member with matching text → `fail`; a member in authoritative mode → counted non-pass; an unknown flag → exit 4 with no spawn. |
| AC-68.13 | unit | **Report and summary.** The report has the header (date, agent, mode, backend version from `health.liveness`, commit, server path, 8 tools, 68 actions — A7); the scorecard per domain; the lifecycle matrix; the Phase 3 functional table; the issues log (severity × tool.action × error × reason); and the `DELTA` summary. Container mode's header states "non-authoritative container subset" (Spec §Where it runs). `mcp-audit-summary.json` validates against `summary.schema.json`. | Zorivest §Output Format; Spec §Evidence | A summary missing `mode` fails schema validation; a container-mode report without the subset banner fails the render test. |
| AC-68.14 | unit | **No secrets on disk.** No token value appears in `actions.jsonl`, the summary, the report or the captured server stderr. | Spec §What this layer must not do ("Store the Bearer token in tool results or logs"); PROFILE E5 | A test seeds known token strings into a step's args, error text and stderr; after writing, a byte search of every output file finds zero occurrences. |
| AC-68.15 | integration | **Authoritative run** on Windows meets `AUTHORITATIVE_ACCEPTANCE`. It writes the first baseline (`recorded_commit` = tested commit) and the report under `.agent/context/MCP/`. Observable: `windows-gate-result.json` stage `mcp-audit` exit ∈ {0, 1} (1 = findings, never 2/3/4) plus the committed summary. Chain: `validate-task.ps1 windows-gate → npm run audit -- --mode authoritative --no-baseline --update-baseline`. | Spec §Where it runs; Human-approved H-3; grouping D-4 | `windows-gate-check` rejects a result whose `mcp-audit` stage is missing or exits 2/3/4, whose summary `mode` is not `authoritative`, whose `cleanup.ok` is false, whose liveness/dependencies/tts.generate are not `pass`, or whose baseline `recorded_commit` ≠ `tested_commit`. `findings-check` (row 12) rejects any non-`pass` baseline entry whose `issue` is missing or not in `known-issues.yaml`, and any baseline change beyond `BASELINE_ANNOTATION_RULE`. |
| AC-68.16 | integration | **Workflow and skill.** `.agent/workflows/mcp-audit.md` and `.agent/skills/mcp-tool-audit/SKILL.md` exist with frontmatter. They are indexed in `.agent/workflows/README.md` and `.agent/skills/README.md`. They describe the triggers, both modes, `ISOLATION_GUARD`, `CLEANUP_PREDICATE`, `BASELINE_UPDATE_RULE`, how findings become known issues (`issue_triage.py add`), and a short manual IDE spot-check. Every `npm run <name>` and flag they cite exists. Chain: doc-test `tests/audit/docs.test.ts` reads both files and `package.json`. | Spec §Deliverables; Zorivest §When to Invoke | The doc-test fails on a cited script or flag that does not exist; a fixture md citing `npm run audit-x` fails. |
| AC-68.17 | unit | **Typecheck covers the runner.** `npm --prefix mcp-server run typecheck` also checks `scripts/**` through `tsconfig.scripts.json`, so the D6 `mcp-types` stage covers it. `.agent/docs/commands.md` §D6 registers a `mcp-audit` runtime row. | Local Canon D6 (`commands.md:204-211`); M4 | Red: before the change, a deliberate type error in `scripts/audit/classify.ts` passes `typecheck` (receipt); after the change, the same error fails it. The error is reverted in the same row. |
| AC-68.18 | unit | **Spec hub reconciled.** None of `STALE_SPEC_PATTERNS` remains in the section. `05-mcp-server.md` §MCP live audit names only real actions (D-5). It states the baseline path, the isolated-backend rule (H-2) and the container-subset wording (D-8). It corrects the `tools-parity`/`action-index` "GUI action index" claim (they compare against `mcp-server/tests/fixtures.ts`). `BUILD_PLAN.md` Phase 5 status is updated at closeout. | Local Canon `registry.ts`, `fixtures.ts`; D3 | `validate-task.sh docs` runs a fixed-string `rg` for each of `STALE_SPEC_PATTERNS` over the extracted section and expects zero hits. Its negative case: the check run against today's section (before row 7) reports hits. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Deliverables, report home, baseline | Spec + Local Canon | 05 §Deliverables; baseline at `.agent/skills/mcp-tool-audit/resources/` (D-9, Zorivest relative path) |
| How the client connects | Spec + Research-backed | 05 §Client; SDK `Client`/`StdioClientTransport` over Inspector CLI (D-2) |
| Which config the client uses | Local Canon | `copyMcpConfig` env (`ipc.ts:392-405`) + `mcp.json.example` command/args → `MCP_LAUNCH` |
| Backend the audit hits | Human-approved | H-2 isolated spawned backend |
| Action names per lifecycle | Spec corrected by Local Canon | 05 names non-existent actions; `ACTION_INDEX` governs (D-5) |
| Observable per step | Spec + Local Canon | G25 + `AUDIT_PLAN` table; the row-3 behaviors (§`AUDIT_PLAN`, last paragraph) pinned from code with file:line |
| Destructive refusal observable | Spec + Research-backed | `REFUSAL_ORACLE`; SDK input-validation error accepted as refusal text (D-4) |
| Container behavior | Spec + Local Canon | Non-authoritative subset with `ENV_BOUND_AUDIT` (D-8, cloud-local §4) |
| Fixtures | Research-backed / Local Canon | `AUDIT_FIXTURES` (D-7) |
| Runner language and location | Local Canon | TS under `mcp-server/scripts/audit/` (D-1) |
| Consolidation score | Local Canon | n/a, consolidation is done (known-issue note; D-10) |
| Sequencing | Human-approved | H-3 build now, baseline later; `SEQUENCING_GATE` before Part B |
| Execution host / gate | pending human | H-4 Decision Brief |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `mcp-server/scripts/audit/{run,backend,client,observer,plan,discovery,classify,ledger,report,redact,fixtures}.ts` | new | Runner (§Runner design) |
| `mcp-server/scripts/audit/{summary,baseline}.schema.json` | new | `mcp-audit-summary.v1`, `mcp-audit-baseline.v1` |
| `mcp-server/tests/audit/{classify,coverage,baseline,isolation,ledger,report,redact}.test.ts`, `run-cli.test.ts`, `docs.test.ts` | new | `UNIT_TESTS`, the CLI half of `RUNNER_TESTS`, `DOC_TESTS` |
| `mcp-server/tests/audit/fake-backend.ts`, `runner-fake-backend.test.ts` | new | Node `http` fake API + built-server integration (AC-68.1/4/6/7/8) |
| `mcp-server/tsconfig.scripts.json` | new | `noEmit`, `rootDir: "."`, includes `scripts/**/*.ts` and `src/**/*.ts` |
| `mcp-server/package.json` | modify (scripts only) | `audit: tsx scripts/audit/run.ts`; `typecheck: tsc --noEmit && tsc -p tsconfig.scripts.json` |
| `.agent/workflows/mcp-audit.md`, `.agent/skills/mcp-tool-audit/SKILL.md` | new | Workflow and skill |
| `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` | new (Part B) | First authoritative baseline |
| `.agent/context/MCP/mcp-tool-audit-report.md` | new (Part B) | First authoritative report |
| `.agent/workflows/README.md`, `.agent/skills/README.md` | modify | Index rows |
| `.agent/docs/commands.md` | modify | D6 `mcp-audit` runtime row |
| `docs/build-plan/05-mcp-server.md`, `docs/BUILD_PLAN.md` | modify | AC-68.18; Phase 5 status at closeout |
| `.agent/context/known-issues.yaml` (+ rendered `.md`) | tool-modify | `MCP-PACKAGED-ENTRY-UNREACHABLE` (hypothesis, row 1); audit findings (row 12); `MCP-LIVE-AUDIT-WORKFLOW` resolved (H2) |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `current-focus.md`, grouping §6 | tool-modify | MEU-68 states |
| `docs/execution/plans/2026-10-01-mcp-live-audit/{walkthrough.md,mcp-test-floor.json,windows-gate-result.json,windows-gate-baseline.json,mcp-audit-summary.json}` | new (execution) | Evidence: walkthrough, row-1 floor, Windows result and its copies of the gate-produced baseline and summary |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Fixing the packaged MCP entry guard and the missing `node_modules` in `resources/mcp-server/` | out-of-scope | — | 05 §MCP live audit Client row targets "the **built** server", and §Deliverables lists no product change; packaging is Phase 7 (`07-distribution.md:236-249`, `ui/electron-builder.yml:32-33`). Filed in row 1 as `MCP-PACKAGED-ENTRY-UNREACHABLE` (hypothesis) for the next triage (D-6) |
| `copyMcpConfig` writing `command`/`args` | out-of-scope | — | `07-distribution.md:246-249` specifies the env-only payload as the contract |
| New MCP actions for REST-only routes (`/captures/requests/{id}/complete\|cancel`, `/health/console`) | out-of-scope | — | 05 §What this layer must not do ("Invent routes or job types…"); `startup-metrics` is Electron-only per the same table. The runner uses REST cancel only for cleanup |
| Live YouTube in the default Vitest suite | out-of-scope | — | 05 §Testing "No live YouTube in the default suite"; the runner is a separate `npm run audit`, never part of `npm test` |
| Upload or any write to YouTube | out-of-scope | — | PROFILE E5, AGENTS §Project Context |
| Zorivest consolidation score, provider/pipeline/tax phases | out-of-scope | — | `_inspiration/_zorivest_mcp_tool_audit_skill.md` header ("domains … are not av-kit scope"); `known-issues.yaml:713-714` (consolidation done) |
| Audit coverage of MEU-67's two new capture actions | deferred | MEU-67 | Grouping §Session 28 "Session 30 adds two MCP actions the audit must then cover — that is a one-line baseline update"; AC-68.5 makes the omission a test failure in Session 30 |
| Fixing product defects the authoritative run finds | out-of-scope | — | 05 §MCP live audit §Deliverables and §Phase 5 (Zorivest) make the audit's output a report and filed issues, not fixes. `AUTHORITATIVE_ACCEPTANCE` files each finding through `issue_triage.py` for the next `/issue-triage` → `/session-grouping`. A finding in MEU-62's surface reopens MEU-62 instead (Stop Conditions) |

## BUILD_PLAN.md Audit

This project modifies `docs/build-plan/05-mcp-server.md` §MCP live audit (AC-68.18) and the Phase 5 status row of `docs/BUILD_PLAN.md` at closeout. `docs/build-plan/build-priority-matrix.md` row 5.3 is checked and needs no change. Validation is `validate-task.sh docs` (row 7) and `post-review-state` (H2-2). The latter asserts the Phase 5 row names MEU-68 approved and that `uv run python tools/meu_status.py render --check` passes.

---

## Verification Plan

`validate-task.sh` (container) and `validate-task.ps1` (Windows) hold every exact procedure, so the `task.md` cells stay lintable. They are written from one stage list (cloud-local §2).

1. **Prerequisites (row 1):** `validate-task.sh prereq` checks node ≥ 18, npm, uv, `npm --prefix mcp-server ci`, `uv sync --frozen`, `npm --prefix mcp-server run build`, and the pre-edit `mcp-tests` count, recorded as `MCP_TEST_FLOOR` in `mcp-test-floor.json` (plan folder) and in the walkthrough. It also re-runs the context-tool check.
2. **Red (row 2):** `validate-task.sh red`. Vitest JSON over all `TEST_SETS` must show failed **assertions**, zero suite-load errors, and every `VITEST_ACS` id in a test title. Interface stubs return neutral values, so no import errors occur. The AC-68.17 typecheck Red is a separate receipt.
3. **Targeted Green (rows 3–4, 7):** `green` runs `UNIT_TESTS` after each production edit; `fake` runs `UNIT_TESTS` + `RUNNER_TESTS` after `npm run build`; `docs` (row 7) runs `DOC_TESTS`.
4. **Static + full MCP (row 5, row 8):** `mcp-types`, `mcp-build`, `mcp-tests` (D6 IDs) plus `scope`.
5. **Container subset run (row 6):** `validate-task.sh audit-container` runs `npm --prefix mcp-server run audit -- --mode container --no-baseline --out "$RECEIPTS_DIR/s28-audit-container"` and asserts the summary: `mode: container`; `cleanup.ok`; every non-pass is a proven `ENV_BOUND_AUDIT` member, `blocked` beneath one, or covered by `MEU62_PENDING_TOLERANCE`; and every domain has at least one `pass`. Each domain has steps that need no created entity (`list`, `voices`, `available`, `sabr_get`, `gpu`, settings, health), and `AUDIT_PLAN` gives them no `depends_on` on a network or model step. The runner may exit 1 only when every `fail` is `MEU62_PENDING_TOLERANCE`-covered.
6. **Pregate (row 10):** the same stages as `WINDOWS_GATE` where they can run in the container. Non-authoritative.
7. **`WINDOWS_GATE` (row 11):** `validate-task.ps1 -Check windows-gate` runs these stages: preflight (quiet machine, `rtk --version`, commit and clean tree, external inputs per Session 26 RULE-2), `mcp-npm-ci`, `uv-sync`, `mcp-types`, `mcp-build`, `mcp-tests`, `mcp-audit` (authoritative, `--no-baseline --update-baseline`, `--out C:/Temp/av-kit/s28-audit`, report to `.agent/context/MCP/`). An optional non-blocking `packaged-probe` runs only with `-PackagedServer <path>`. Zero tolerance. External inputs (`P:/agentic-framework` HEAD, the `P:/.agent` registry hash) are **recorded, not compared**: no stage of this gate reads them (there are no py-tests and no framework-adoption tests). That is the documented basis for departing from cloud-local §3.2's "stop on drift". A mismatch with attempt N−1 is noted in the walkthrough, not a preflight failure.
8. **`windows-gate-check` (row 11):** schema `s28-windows-gate.v1`; `clean_tree`; exact stage order; every blocking stage exit 0 except `mcp-audit`, which may exit 1 (findings) but never 2/3/4; `mcp-tests` total > `MCP_TEST_FLOOR` (the audit tests are added), 0 failed; the summary is authoritative with `cleanup.ok` and the three must-pass actions `pass`; baseline `recorded_commit` = `tested_commit` and byte-equal to `windows-gate-baseline.json`; code identity over `GATED_PATHS` (cloud-local §3.3).
9. **`findings-check` (row 12):** `BASELINE_ANNOTATION_RULE`, plus every non-`pass` entry's `issue` exists in `known-issues.yaml` (`AUTHORITATIVE_ACCEPTANCE`).
10. **OpenAPI:** no `packages/api/` change is planned. H1-4 proves `git diff` over `packages/` is empty, which is the skip-with-basis for G8. If anything there changes, the plan stops (Stop Conditions).

## Stop Conditions

Stop and wait for a human when:

- `SEQUENCING_GATE` refuses at row 9. This is a planned `[B]` (dependency), not a failure.
- `scope` finds a change outside `PART_A_PATHS` in Part A, or any change under `packages/`, `ui/` or `mcp-server/src/` at any point. A real product defect the runner finds goes to a known issue; it is not fixed here.
- Red is not an assertion Red.
- An `ENV_BOUND_AUDIT` candidate cannot be proven. It stays a failure; do not widen the census by assertion.
- At row 9, MEU-62's runtime assets (spaCy model, ONNX vocab) cannot be provisioned in a fresh `ISOLATED_ROOT` through MCP actions. Grouping D-1 makes them managed downloads, so `tts.generate` cannot be must-pass without them. That is an M2 gap to brief (MCP action or documented REST pre-seed), not a silent pre-seed.
- The authoritative run finds a `fail` in MEU-62's surface (`tts.*`, `models.*` runtime assets). That reopens MEU-62 through a Decision Brief; it is not filed as a new issue against a closed MEU.
- `WINDOWS_GATE` fails for a non-product reason (cloud-local §3.5 Decision Brief).
- Plan review reaches 3 rounds, or execution review reaches 6.

Never commit, push or merge without the execution authorization in [human-gate-decision.md](human-gate-decision.md). Never open a PR, merge to `main`, release or deploy.

---

## Decision Log

Research engine for this session: `native` (Claude Code `WebSearch`). Grouping carry-forward D-2, D-4 and D-5 enter the reflection's Decisions Log with stage `grouping`.

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
```

### H-4 — Execution authorization and gate location

**Recommendation:** split like Sessions 25 and 26. Part A (rows 1–8, 10) runs in this container. Part B's authoritative run (row 11) is one Windows `WINDOWS_GATE` that Mat triggers with `validate-task.ps1 -Check windows-gate`. The rows touching user input (11) are the planned turn boundaries. **Reversibility:** two-way. **Default if unanswered:** no execution (SIGN 1; `plan_to_exec_gate: human`).
**Precedents:** `docs/execution/plans/2026-09-28-p11-capture-settings/human-gate-decision.md:1-40` ("Split like Session 25 (Recommended)"); `.agent/docs/cloud-local-collaboration.md` §2–§3. **Research:** none needed; this is a local-process choice.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| A. Split: container Part A + one Windows `WINDOWS_GATE` (recommended) | cloud-local §2; Session 26 | — | — | ✅ |
| B. Everything on the Windows host (local agent runs all rows) | PROFILE A4 Windows; Session 24 native baseline | One machine, `rtk` everywhere | Needs a local agent session for every row; Part A has no Windows-only step, so it gains nothing | ⚠️ |
| C. Container only, no Windows run | — | No human round trip | The baseline would be non-authoritative, contradicting 05 §Where it runs, so MEU-68 could not close | ❌ |

## Round 1 Review Corrections

Review: `.agent/context/handoffs/2026-10-01-mcp-live-audit-plan-critical-review.md`, Round 1, `changes_required` (3 High, 4 Medium, 2 Low). Every finding was applied through `/plan-corrections`, with no code change.

| Finding | Correction |
|---|---|
| F1 High: rows 3–4 ran tests that need rows 5–7 | New `TEST_SETS`: `green` = `UNIT_TESTS`, `fake` = `UNIT_TESTS` + `RUNNER_TESTS`, `docs` = `DOC_TESTS`. Only Red and `gate-a`+ run everything. The AC-68.12 CLI tests move to `run-cli.test.ts` (row 4). |
| F2 High: `SEQUENCING_GATE` grepped YAML text from a JSON printer | `meu_status_is` parses the `meu_status.py get` JSON (`tools/meu_status.py:98-108`). It is used by `prereq`, `seqgate`, `ssot-review` and `post-review-state`. Plan-local proof: `MEU-62` → `pending`, predicate exit 1; `MEU-18` → `approved`, exit 0. |
| F3 High: row 6 hit MEU-62's TTS defect | New `MEU62_PENDING_TOLERANCE`: script-side, container-only, signature-bound, and off once MEU-62 is approved. The runner still reports `fail`. The "None of it needs MEU-62" sentence is replaced. |
| F4 Medium: `tts.output_path` missing from the guard | `ISOLATION_KEYS` is derived structurally from the settings schema (six keys, `settings.ts:16,29,40,44,58,64`). An unmapped new path key fails closed, with a unit negative case. |
| F5 Medium: transcript `requeue`/`retry` from illegal states; tts cancel race | Transcript: legal-state calls per `TRANSCRIPT_PARENT_TRANSITIONS` plus a 409 conflict-contract call on a Done job; the reachable sequence is pinned at row 3, and an unreachable one is a Stop Condition. TTS: `tts_long_text` plus a non-terminal precondition read, re-established once. |
| F6 Medium: hub check false-passes; per-domain assertion absent | `post-review-state` requires `MEU-68 approved` on the Phase 5 row. `audit_container_assert` requires at least one `pass` per domain; the plan text now matches. |
| F7 Medium: SSOT conflict at the row-9 merge | New `SSOT_MERGE_RULE` (take `origin/main`, re-apply through tools, render). `seqgate` runs both render checks. |
| F8 Low: clerical | H-1 location; 05:303; §Verification numbering; the `red` comment; one `STALE_SPEC_PATTERNS` definition used by both plan and script, with its negative case proven against today's section (rg exit 0, 3 hits); the queue-level `cancel` wording; the "per finding" row relabelled `out-of-scope` with a Basis. |
| F9 Low: AC-68.15 had no Vitest test; external inputs were not compared | `VITEST_ACS` excludes AC-68.15/17/18 from the Red title check. The external inputs are recorded but not compared, with the basis stated (no gate stage reads them). |

Blast-radius census (Step 5c): every old literal is gone from `implementation-plan.md`, `task.md` and `validate-task.sh`, with zero hits for each of: "None of it needs MEU-62", "status: approved", "cancel` url_b", "cancel` job 2", "9a.", "§Pending", "05-mcp-server.md:302", "| deferred | per finding", "AC-68.1–68.16", "→status→", "Part A writes nothing", "stubs must compile", "requeue` → `retry`". Each new name resolves in every file that uses it: `MEU62_PENDING_TOLERANCE` (plan 3, task 1, sh 3), `TEST_SETS` (2/1/1), `SSOT_MERGE_RULE` (3/1/1), `STALE_SPEC_PATTERNS` (plan 2, sh 3), `ISOLATION_KEYS` (plan 1, task 1), `VITEST_ACS` (2/1/3), `tts_long_text` (plan 2). `bash -n validate-task.sh` passes; `lint_task_contract.py` passes (21 rows).

## Round 2 Correction Notes (post-approval, non-blocking)

Round 2 verdict `approved`, with 1 Medium and 4 Low notes. They were applied as plan text only, following the Session 26 precedent (`2026-09-28-p11-capture-settings/implementation-plan.md` §Round 2 Correction Notes):

- **R2-1:** `OBSERVABLE_RULE` defines a step's `error` field and the `blocked_by` dependents, so `MEU62_PENDING_TOLERANCE` matches the TTS job's `error_message`.
- **R2-2:** the `ISOLATION_GUARD` predicate is owned by `classify.ts` (row 3).
- **R2-3:** a candidate transcript sequence reaches Cancelled through `pause` → `stop`, to be confirmed at row 3.
- **R2-4:** `converter.output_dir`; the row-3 wording; the `task.md` names list now includes the Round 1 contracts. The Round 1 census receipt is `${RECEIPTS_DIR}/s28-census-r1.txt`. The old literals appear in the final plan only as quotations inside §Round 1 Review Corrections.
- **R2-5:** `meu_status_is` writes stderr to a separate `.err` file.

The reviewer's out-of-contract observations were also adopted:

- a row-9 Stop Condition for MEU-62 assets that MCP cannot reach;
- `tts.generate` MP3 added to the ffmpeg census row;
- the summary schema pins `steps[].tool` to the 8 compound tools;
- the `--no-baseline` / `--baseline` semantics;
- `uv` runs with the repo-root cwd.

## Execution amendments — 2026-10-01

| ID | Amendment | Basis | Authority |
|---|---|---|---|
| A1 | `uv sync --frozen` becomes `uv sync --frozen --all-packages` in `validate-task.sh` (`prereq`, `pregate`) and in `validate-task.ps1` (`uv-sync` stage). | Row 1: the root `pyproject.toml` sets `package = false` with `dependencies = []`, so a plain sync installs only the dev group ("Audited 19 packages"), and `import avkit_api` fails with `ModuleNotFoundError`. With `--all-packages`, the workspace members install and the import succeeds (yt-dlp 2026.07.04). The runner spawns `python -m avkit_api`, so the backend must be importable. | Defect in a plan-authored command, not a behavior change. The `.ps1` is a `GATED_PATHS` file and is not yet tested, so no gate reopens. |
| A2 | **Filed findings.** The summary gains `discovery.findings[]` (`{code, tool, detail}`) for tool-level discovery results; AC-68.3 is unchanged (a schema/meta disagreement is a discovery `fail`). The served action set is read from `_meta.action_descriptions`, the only machine-readable action list the server publishes. New single-statement name `FILED_FINDINGS`: a finding code → known-issue id map in `validate-task.sh`, with `schema_not_advertised` → `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`. `audit-container`, `windows-gate-check` and `findings-check` tolerate a discovery `fail` or runner exit 1 only when every finding's code is in `FILED_FINDINGS` and its issue id exists in `known-issues.yaml`. The baseline records `findings[]` with `issue`, and `BASELINE_ANNOTATION_RULE` covers them. `AUTHORITATIVE_ACCEPTANCE` already requires a filed issue for every non-pass item. | Row 2 probe (SDK `Client` over stdio against `dist/index.js`): all 8 tools list `inputSchema` `{"type":"object","properties":{}}`, because SDK 1.30.0 `normalizeObjectSchema` drops the per-tool Zod union (`sdk/dist/esm/server/mcp.js:76-83`). `_meta.action_descriptions` lists 67 actions, and the refusal text is `Input validation error: … expected true at confirm` (D-4 confirmed). Filed as `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` (open, high). Fixing it changes `mcp-server/src`, which is outside `PART_A_PATHS` (§Stop Conditions: a product defect goes to a known issue). | Execution decision D-12 (autonomous, two-way): the AC is unchanged. Only the plan-authored gate expectation, which assumed a clean discovery, is corrected. |
| A3 | **Pre-Red FIC corrections (no test written yet).** (a) AC-68.1's negative oracle: with `AVKIT_API_TOKEN` omitted, `tools/list` still succeeds, because it needs no token. `token_missing` therefore surfaces on the first tool call, the isolation snapshot (`avkit_settings.get`): `isolation.ok: false`, exit 3, no lifecycle call made, and `launch.initialized` true. The plan text "discovery is `fail` and exit 1" was wrong about the mechanism. (b) AC-68.4's 9th-tool negative is a unit test over `classifyDiscovery`, because the real built server cannot be made to serve a 9th tool. (c) AC-68.2's patterns live once in `mcp-server/tests/audit/forbidden-imports.txt`. Both `validate-task.sh scope` (`rg -f`) and `run-cli.test.ts` read that file (single-statement rule). | Row 2 probe: `tools/list` returned all 8 tools with `AVKIT_APP_DATA` pointing at a non-existent folder and a dummy token. A tool call without a backend returned `app_not_running`. Neither AC's positive contract changes. | Execution decision, logged before the Red; AGENTS §Testing: expectations are fixed before Red, not edited in Green. |
| A4 | **Row-3 pins from the live backend.** (a) `AUDIT_FIXTURES.transcript_source_url` becomes `https://www.youtube.com/watch_videos?video_ids=jNQXAC9IVRw,dQw4w9WgXcQ,9bZkp7q19f0,kJQP7kiw5Fk`, a fixed 4-video anonymous playlist (yt-dlp `youtube:tab`, 2 entries verified for the 2-id form). It replaces `@jawed`. Isolated transcript settings are `delay_between_requests: 3` and `max_retries: 0`. (b) A third download fixture, `download_url_c` (`aqz-KE-bpKQ`, Big Buck Bunny, 10 min), is the cancel target. (c) The container capture seed uses REST register mode with `source: "scan"` (the `RegisterSourceWire` values are hotkey/gui/scan). (d) The backend version comes from `GET /openapi.json` `info.version`, because `/health` returns only `{status}`. (e) REST statuses are `Pending/Processing/Done/Cancelled/Failed` (not Queued/Completed). (f) The `ENV_BOUND_AUDIT` signatures were fixed from real container errors: `capture.capture` gives `internal_error` (HTTP 503; the domain text "screen capture requires Windows" is masked, `errors.py:76-94`) with proof `platform != win32`; `download.add`/`transcript.add` give `internal_error` (500) with proof that a direct yt-dlp extract fails with "Sign in to confirm you’re not a bot". `models.download` works in the container (Hugging Face reachable). | Row 3 probes on a real `avkit_api` in a scratch app-data folder (walkthrough §Row-3 pins). Three product defects were filed on the way: `API-UNHANDLED-ERROR-OPAQUE`, `MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES` (plus `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` from row 2). | Execution decision D-13 (autonomous, two-way): fixtures and sequences follow the code's state machines; no AC changes. |
| A5 | **AC-68.1 env wording.** "Only the env keys named in `MCP_LAUNCH` reach the child" applies to the launch config the runner (like an IDE's `mcp.json`) specifies, and that is what `buildLaunch` and `summary.launch.env_keys` assert. SDK 1.30.0 `StdioClientTransport` also merges its own `DEFAULT_INHERITED_ENV_VARS` (`sdk/dist/esm/client/stdio.js:8-33,67-70`: HOME/LOGNAME/PATH/SHELL/TERM/USER; on Windows APPDATA/LOCALAPPDATA/USERPROFILE and so on), as every SDK-based IDE client does. None of those keys is `AVKIT_*`, so isolation (no inherited `AVKIT_API_BASE`) still holds. | Row 4 implementation reading of the SDK transport. | Execution decision, wording only; the tests are unchanged. |
| A6 | `PART_A_PATHS` gains `.agent/context/handoffs/2026-10-01-mcp-live-audit-*`: the project's own plan review, handoff and implementation review. | `scope a` at row 5 flagged the committed plan review (`569619a`), which the definition had omitted. | Clerical; same-project artifact. |
| A7 | **MEU-62 added a 68th action.** The row-9 merge of `origin/main` (Session 27, `0e18fbd`) brought `avkit_models.download_asset` (`asset` ∈ `tts_onnx_vocab`, `tts_spacy_model`; `POST /models/download {asset}`; registry.ts appends it after the capture rows). `AUDIT_ACTION_SET` is now 68. `AUDIT_PLAN` gains `models.download_asset.vocab` and `models.download_asset.spacy`: each reads the asset's row in `/health/dependencies` (`state` ready/missing/downloading). A `ready` asset must answer 409 with the state unchanged; a missing one must be accepted and reach `ready`. `tts.generate` depends on both. Two test expectations change, both tied to the registry count: `coverage.test.ts` (67 → 68) and the fake-backend discovery count. `validate-task.sh` states the count once as `AUDIT_ACTION_COUNT=68`. This also clears the row-9 Stop Condition "MEU-62 assets not reachable through MCP": they are reachable. | `git diff HEAD MERGE_HEAD -- mcp-server/src packages/api` at the row-9 merge (`76465a0`); `packages/infrastructure/src/avkit_infra/tts/assets.py` stores assets under `tts.models_directory`, which is already an `ISOLATION_KEYS` member. | Source-backed expectation amendment; the dependency's own spec change, approved in Session 27. Flagged for the execution reviewer (AGENTS §Testing: a proven expectation change needs an amendment plus independent review). |
| A8 | **Synchronous TTS (filed `MCP-TTS-GENERATE-SYNCHRONOUS`, high).** `POST /tts/generate` synthesizes inline and returns only when the job ends, and the MCP client times out at 30 s (`client.ts:14`). No client therefore ever holds the id of a running job. Changes: the `tts.generate.job2` step and `tts_long_text` are removed. `tts.cancel` runs the REFUSAL_ORACLE on the finished job 1: both refusals must hold, and the confirmed call has no effect on a Done job, so the step fails with `confirmed_no_effect`. That failure carries the filed issue. A new single-statement name, `FILED_STEP_FAILURES` (`validate-task.sh`), maps `avkit_tts.cancel` → [`confirmed_no_effect`, `MCP-TTS-GENERATE-SYNCHRONOUS`]. `audit-container` tolerates a step failure only when both its reason and the issue's existence match; the authoritative run records it through `findings-check`. `tts_text` is shortened to 28 characters (12.5 s for 66 characters on container CPU), and `models.load` uses `device: auto`. | Row 10 pregate: `tts.generate` (66 chars) Done in 12,531 ms with a valid MP3; the job2 MCP call returned `fetch_failed` at 30,005 ms. Source: `routes/tts.py:54-69`, `services/tts.py:110-200`. | Execution decision D-14 (autonomous, two-way): a product defect is reported, not worked around. When the API exposes a running job, the step becomes a cancel of that job. |
| A9 | **Transcript fixture.** `transcript_source_url` becomes `https://www.youtube.com/playlist?list=PLav47HAVZMjnA3P7yQvneyQPiVxZ6erFS` (Blender Studio, "Live: Rigging Snow", 9 videos). It replaces A4a's `watch_videos` anonymous list. Separately, the `ENV_BOUND_AUDIT` network proof is now per failing URL: each failing `download.add.*` / `transcript.add` step's own fixture URL must also fail a direct yt-dlp extract (`NETWORK_STEP_URLS` in `plan.ts`), not just `download_url_a`. | Row 10 pregate: the backend `YouTubeAdapter.extract_video_ids`/`extract_info` raise `AttributeError: 'NoneType' object has no attribute 'get'` on the `watch_videos` URL, so it would fail on Windows too. Three Blender Studio playlists extract through the adapter in the container (3/9/4 ids, `PlaylistInfo`). The bot check hit `url_c` and the playlist while `url_a` extracted fine in the same run; the coarse proof correctly refused to tolerate them, and it was made precise. | Execution decision (two-way fixture; fail-closed proof kept). |
| A10 | In the Decision Log, D-6's precedent quotes the example path as `$RESOURCES/mcp-server/index.js` instead of the brace form. | H1-5: `validate_closeout_artifacts.py` reads a `{NAME}` token in a decision record as an unfilled template placeholder and refuses the record. The reflection reconciles against this plan, so the H2-1 check would refuse it too. The prose quotation at §User Review Required keeps the file's literal text. | Clerical; no decision content changes. |
| A11 | **Execution-review round 1 corrections (F1–F4).** (a) F1: `transcript.resume` polls until an item is terminal, restoring this plan's transcript-row observable that the implementation had dropped. The poll ends on a fetched transcript (`transcripts_done ≥ 1`) or a `Failed` item (`last_item_status`); a `Skipped` item (no captions) lets the worker try the next video. `transcript.compile` requires `transcripts_done ≥ 1`, and the volume's `## Contents` entries must equal it. An empty volume is `hollow` ("no transcript fetched"). `transcript.requeue.conflict` restores the row's 409 contract for `requeue` (97 steps). (b) A new `ENV_BOUND_AUDIT` member, `avkit_transcript.compile`: signature `^no transcript fetched`; proof: the product's `TranscriptAdapter` raises the retryable block error for the source's first video (missing captions do not count). Container only. (c) F2: a missing `--baseline` file is exit 4 before any spawn, with or without `--update-baseline`. (d) F3: `coverage.test.ts` checks the committed baseline against `AUDIT_ACTION_SET`, and that every non-pass entry and every finding carries an `issue`. (e) F4: `windows-gate-check` aggregates worst-of per action; `validate-task.ps1` records `audit.steps`. (f) A sibling found while re-running: a backend that never prints `AVKIT_READY` is killed before the error propagates (`startBackendProcess`). | Review `…-implementation-critical-review.md` round 1. Container probes: the worker checks `_pause` before item 0 (`transcript.py:415-420`), so Paused never proved a fetch, and D-18's "no captions" cause was wrong. youtube-transcript-api is IP-blocked from the container (`RequestBlocked`). A never-ready backend kept node alive until the 590 s timeout. | Corrections under `GATED_PATHS` reopen `WINDOWS_GATE` (attempt 2) per task row H1-6. The oracle is restored to the approved contract, not weakened. |
| A12 | Review round 2, R2-1: `coverage.test.ts` asserts that the committed baseline exists (it used to return early). The plan's F5 Stop-Condition reading of `tts.cancel` (D-14) is ratified by Mat (`human-gate-decision.md` §F5). | Round-2 recheck in `…-implementation-critical-review.md`. Red: with the baseline file absent, the old test passed 8/8 and the new one fails (`expected false to be true`). | Human: "Fix now + attempt 3". The test sits under `GATED_PATHS`, so `WINDOWS_GATE` attempt 3 runs. |
| A13 | `ENV_BOUND_AUDIT` `avkit_download.cancel`. The signature also matches `HTTP Error 403: Forbidden`. The proof becomes the container host **and** a direct yt-dlp test fetch of `download_url_c` failing with the same wall (`mediaFetchBlocked`); before this, the host alone counted (review round 1 OOC-2). | Attempt-3 pregate on `9e186da`: `download.cancel` failed with `ERROR: unable to download video data: HTTP Error 403: Forbidden` (`signature_matched: false`). The census refused it, correctly. A direct yt-dlp fetch from the container reproduced the 403 for `aqz-KE-bpKQ` and `jNQXAC9IVRw`; Windows downloaded both in attempts 1 and 2. | Container-only tolerance with a stronger proof. Authoritative mode tolerates none of it. Tests: `transcript-oracle.test.ts` (403 and bot text with proof → skip_env; no proof, win32, authoritative, or another error → fail). |
| A14 | **H2-1 decision sources.** The reflection reconciles against the plan, the MEU-68 handoff and `MCP-LIVE-AUDIT-WORKFLOW` (`--decision-issue`); the grouping is no longer a `--decision-source`. Grouping D-2, D-4 and D-5 still enter the reflection's Decisions Log, under the IDs `G-D-2`, `G-D-4` and `G-D-5` with stage `grouping`. The handoff's execution decision formerly numbered D-20 is renumbered D-22. Clerical: the AC-68.13 prose says 68 actions (A7). The issue's D-21 record in `known-issues.yaml` is rewritten in the closeout validator's YAML subset (a quoted `chosen`, flow-style lists); the parsed values are identical. | `validate_closeout_artifacts.py` keys decisions by ID across sources and refuses one ID recorded with two stages. This plan's D-1…D-7 (`planning`) reuse the shared grouping's §8 D-1…D-7 (`grouping`), and the issue's enrichment records D-20/D-21 (`triage`). The plan declares no `grouping_source`, so the grouping is optional as a source. | Clerical/process; no decision content changes. Found at H2 prep; review round 3 OOC-4 (67 → 68). |

## Research References

- `docs/build-plan/05-mcp-server.md:287-304` (§MCP live audit), `:85-97` (§Destructive), §Testing, §What this layer must not do.
- `_inspiration/_zorivest_mcp_tool_audit_skill.md` §Phase 1–5, §Cleanup Contract, §Output Format.
- `.agent/docs/emerging-standards.md:844` G25; M3, M4 (`:48-64`).
- `.agent/docs/cloud-local-collaboration.md` §1–§5, §8–§10.
- `docs/execution/reflections/2026-09-28-p11-capture-settings-reflection.md` §Next Session Design Rules. RULE-2 (preflight external inputs) applies to `validate-task.ps1`. RULE-1 and RULE-3 do not apply: there is no drag and no focus strip.
- MCP TypeScript SDK input validation: https://github.com/modelcontextprotocol/typescript-sdk/issues/2879; SDK server docs https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/server.md.
- MCP Inspector CLI: https://github.com/modelcontextprotocol/inspector/blob/main/clients/cli/README.md.
- Fixture source: https://en.wikipedia.org/wiki/Me_at_the_zoo.

## Validation stage contract

- **Static:** `mcp-types` (with `tsconfig.scripts.json`), `scope` (`PART_A_PATHS`, AC-68.2 rg), `task-contract`.
- **Targeted:** `tests/audit/` Vitest after each edit; the fake-backend integration after each `mcp-build`.
- **Full (container, non-authoritative):** `mcp-build` → `mcp-tests` → `audit-container`.
- **Runtime (authoritative):** `WINDOWS_GATE` on Mat's host, zero tolerance, bound to a commit.
- **Input identity:** git HEAD, `git diff --stat`, SHA-256 of `mcp-server/package-lock.json` and `uv.lock`, node, npm, uv and Python versions, recorded in `walkthrough.md` before each full run. `windows-gate-result.json` carries `tested_commit`, the lockfile hashes and the versions. Any change under `GATED_PATHS` after `tested_commit` invalidates the run (§3.4).
- **Freshness:** Red/targeted receipts are working evidence. Only the `WINDOWS_GATE` result on the final reviewed tree certifies H1-2.
