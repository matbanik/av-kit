---
name: MCP Tool Audit
description: Live end-to-end audit of every av-kit MCP compound-tool action, driving the built server over stdio (as an IDE does) against an isolated real backend, asserting observable state through REST and the filesystem, diffing a committed baseline, and cleaning up. Use after mcp-server or API changes, before a release, or on demand via /mcp-audit.
---

# MCP Tool Audit Skill

Adapted from the Zorivest MCP Tool Audit protocol (`_zorivest_mcp_tool_audit_skill.md`, which isn't published with this repository). The shape transfers; the domains, the confirmation model and the consolidation score do not. Spec: [`docs/build-plan/05-mcp-server.md` §MCP live audit](../../../docs/build-plan/05-mcp-server.md#mcp-live-audit-residual) (MEU-68). The runner lives in `mcp-server/scripts/audit/`.

## When to Invoke

| Trigger | Reason |
|---|---|
| After a change under `mcp-server/src/` | New or changed actions need a live check; the Vitest suites stub HTTP |
| After an API route, schema or service change in `packages/` | The MCP surface can break without any MCP code change |
| Before a release or a version bump | Every action must work end to end from an IDE |
| After a known issue linked to an MCP action is fixed | The baseline records it as FIXED |
| On demand via `/mcp-audit` | Routine health check |

## What it proves (and what it does not)

- **It proves** that each action in `ACTION_INDEX` (68 as of MEU-62) (`mcp-server/src/toolsets/registry.ts`) works through the real stdio server against a real backend with real state. Every step passes only when an **independent observation** holds: a REST read with the GUI token, or a file on disk. An MCP success whose observable is missing is a `hollow` failure (G25, `.agent/docs/emerging-standards.md`).
- **It proves** that every destructive action (`DESTRUCTIVE_ACTIONS`, `mcp-server/src/destructive.ts`) is refused both without `confirm` and with `confirm: false`, with the state unchanged, and that `confirm: true` changes it (REFUSAL_ORACLE).
- **It does not** replace `npm --prefix mcp-server run test` (fast, mocked contracts), and it does not fix what it finds. Every finding becomes a known issue.

## Modes

| Mode | Where | Authority | Tolerance |
|---|---|---|---|
| `container` | Linux container (cloud agent) | **non-authoritative subset**; the report header says so | Only `ENV_BOUND_AUDIT` members (`scripts/audit/census.ts`) whose signature **and** environment proof both match become `skip_env`; their dependents are `blocked`. Everything else fails closed. |
| `authoritative` | Windows host with real Kokoro, ffmpeg, screen capture and network | The only mode that may write the baseline | None. Every non-pass counts. |

## Isolation and cleanup

- **Isolated backend.** The runner spawns its own `python -m avkit_api` (the Electron dev argv) with app-data in a fresh temp root. It never attaches to the user's running app, because `clear` and `remove` would destroy real queues and inbox files (human decision H-2, 2026-10-01).
- **ISOLATION_GUARD.** Before the first lifecycle call, every path-like settings key in `avkit://settings/schema` (`ISOLATION_KEYS`) is set under `<root>/out/` and re-read through REST. Any path outside the root, or a new path key with no mapping, refuses the run with exit 3 before anything is created. `downloader.ffmpeg_path` and `downloader.cookie_file_path` are inputs and are never written.
- **CLEANUP_PREDICATE.** At the end:
  - every created job, shot and request is removed or cancelled through REST;
  - the REST counts of downloads, transcripts, conversions, captures and pending capture requests are all zero;
  - settings equal the post-guard snapshot;
  - the backend process has exited;
  - the root is deleted (unless `--keep`).

  Anything left over is a named residual, and the exit code is 1.

## Baseline

- File: `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`, schema `mcp-audit-baseline.v1` (`scripts/audit/baseline.schema.json`).
- **BASELINE_UPDATE_RULE.** `--update-baseline` writes it only when all of these hold: `--mode authoritative`, `win32`, clean cleanup, and no REGRESSION or REMOVED delta. Otherwise the run exits 2 and the file stays byte-identical. The first recording passes `--no-baseline --update-baseline`.
- **Delta per action:** pass → non-pass is `REGRESSION`; fail → fail is `KNOWN` (it carries the entry's `issue`); fail → pass is `FIXED`; absent → `NEW`; baselined but not served is `REMOVED`.
- After an authoritative run, the only allowed edit is setting `issue` on non-pass entries and findings to filed known-issue ids (`BASELINE_ANNOTATION_RULE`).

## Protocol

1. **Discovery (Phase 1).** `tools/list` must serve exactly the 8 `COMPOUND_TOOLS`. The served action set is `_meta.action_descriptions`. The runner also checks that each tool's advertised `inputSchema` exposes those actions; if not, that is a `schema_not_advertised` finding. Removed, ghost (listed but not callable) and unexpected tools are findings too.
2. **Lifecycles and functional checks (Phases 2–3).** The order is `AUDIT_PLAN` (`scripts/audit/plan.ts`): settings → health → models → tts → downloads → transcripts → convert → capture. The sequences follow the backend state machines, pinned in `docs/execution/plans/2026-10-01-mcp-live-audit/walkthrough.md` §Row-3 pins. For example, transcript `requeue` and `retry` are reached from Cancelled via pause → stop, and a deliberate `retry` on a Pending job must return the 409 conflict envelope.
3. **Regression (Phase 4).** Each action's worst verdict is diffed against the baseline.
4. **Report and record (Phase 5).**
   - `mcp-audit-summary.json` (`mcp-audit-summary.v1`), `actions.jsonl`, `server-stderr.txt` and the Markdown report, all token-redacted.
   - Every new finding is filed with `uv run python tools/issue_triage.py add --id … --severity … --component mcp-server|api|core …`, then `uv run python tools/issue_triage.py render`. A container-only runtime cause is filed as a hypothesis until the target confirms it (`.agent/docs/cloud-local-collaboration.md` §7).

## Running it

| Purpose | Command (from the repo root; build first with `npm --prefix mcp-server run build`) |
|---|---|
| Container subset (cloud agent) | `npm --prefix mcp-server run audit -- --mode container --no-baseline --out <dir> --agent <name>` |
| Authoritative check against the baseline | `npm --prefix mcp-server run audit -- --mode authoritative --baseline <abs path to baseline-snapshot.json> --report <abs path to .agent/context/MCP/mcp-tool-audit-report.md> --out <dir> --agent <name>` |
| Record or replace the baseline (authoritative, Windows) | `npm --prefix mcp-server run audit -- --mode authoritative --no-baseline --update-baseline --baseline <abs path> --report <abs path> --out <dir>` |
| Probe an installed server (discovery only) | `npm --prefix mcp-server run audit -- --mode authoritative --discovery-only --no-baseline --server <install>/resources/mcp-server/index.js --out <dir>` |
| Override a fixture | `npm --prefix mcp-server run audit -- --mode container --no-baseline --fixture download_url_a=<url>` |

The Python backend must be importable: `uv sync --frozen --all-packages`. Paths must be absolute, because `npm --prefix` runs the script with cwd `mcp-server/`. Exit codes: 0 clean, 1 failures/findings/residuals, 2 baseline refused, 3 isolation refused, 4 runner or CLI error.

## IDE spot-check

The audit is a scripted stdio client: the same transport and env shape an IDE uses, but not an IDE. After an authoritative run, a human can confirm the IDE path by hand in two minutes:

1. In Settings, use **Copy MCP config**, and wire it into the IDE's `mcp.json` with `command: node`, `args: [<repo>/mcp-server/dist/index.js]`.
2. Ask the IDE agent to call `avkit_health` (`liveness`, then `dependencies`), then `avkit_settings` (`get`, namespace `ui`).
3. Compare the answers with the Settings page. A mismatch is a finding; file it as above.

## Reading the report

| Section | Meaning |
|---|---|
| Scorecard | Pass, fail, skip_env and blocked counts per tool |
| Lifecycle matrix / Functional results | One row per step, with the observable that decided it |
| Issues log | Every non-pass step with its reason (`hollow`, `unexpected_error`, `refusal_missing`, `refusal_mutated`, `precondition_lost`, …) and the decisive error |
| Discovery findings | Tool-level problems; each needs a filed issue |
| Regression delta | Changes against the baseline |
| Cleanup / Isolation | Residuals, and where every output went |

## Related files

- Workflow: [`.agent/workflows/mcp-audit.md`](../../workflows/mcp-audit.md)
- Runner: `mcp-server/scripts/audit/` (tests in `mcp-server/tests/audit/`)
- Baseline: [`resources/baseline-snapshot.json`](resources/baseline-snapshot.json) (recorded by the first authoritative run)
- Report: `.agent/context/MCP/mcp-tool-audit-report.md`
- Known issues: `.agent/context/known-issues.yaml` (`MCP-LIVE-AUDIT-WORKFLOW` and the findings it filed)
