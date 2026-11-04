---
description: Run the live MCP tool audit — every av-kit compound-tool action through the built stdio server against an isolated real backend, with observable-state checks, baseline diff, cleanup and a report. Container runs are a non-authoritative subset; the authoritative run is on the Windows host.
---

# MCP Audit Workflow (`/mcp-audit`)

Procedure: [`.agent/skills/mcp-tool-audit/SKILL.md`](../skills/mcp-tool-audit/SKILL.md). Read it before running. Spec: `docs/build-plan/05-mcp-server.md` §MCP live audit (MEU-68).

// turbo-all
// NOTE: the audit spawns a backend and downloads a model and media. It writes only under its temp
// root and the --out directory, and never touches the user's app data (ISOLATION_GUARD).

## Steps

1. **Decide the mode.**
   - If the driver OS is not Windows (a cloud container), run `container` mode only. The result is a non-authoritative subset (`.agent/docs/cloud-local-collaboration.md` §1–§4).
   - An authoritative run needs the Windows host. It goes in as a `WINDOWS_GATE`-style request in the cloud-local §5.1 shape, unless a local agent is the driver.
2. **Prepare.** Run `npm --prefix mcp-server ci`, `uv sync --frozen --all-packages`, and `npm --prefix mcp-server run build` (M4: the audit drives `dist/`).
3. **Run.**
   - Container: `npm --prefix mcp-server run audit -- --mode container --no-baseline --out <abs dir> --agent <name>`
   - Authoritative, against the committed baseline: `npm --prefix mcp-server run audit -- --mode authoritative --baseline <abs .agent/skills/mcp-tool-audit/resources/baseline-snapshot.json> --report <abs .agent/context/MCP/mcp-tool-audit-report.md> --out <abs dir> --agent <name>`
   - Recording or replacing the baseline adds `--update-baseline`, and `--no-baseline` the first time. Only an authoritative Windows run with clean cleanup and no regression may write it (BASELINE_UPDATE_RULE).
4. **Read the exit code and the summary** (`<out>/mcp-audit-summary.json`, `mcp-audit-summary.v1`):
   - 0 clean;
   - 1 findings, failures or cleanup residuals;
   - 2 baseline write refused;
   - 3 isolation refused (nothing was created);
   - 4 runner or CLI error.
5. **File every finding.** Each non-pass step and each discovery finding gets a known issue (`uv run python tools/issue_triage.py add …`, then `render`). A `KNOWN` delta already has one. After an authoritative run, set `issue` on the matching baseline entries; nothing else in the baseline may change.
6. **Report.**
   - Authoritative: commit the report and the baseline with the run's commit noted. For a gate, also commit the result files the plan names.
   - Container: keep the summary in the plan's evidence, never as the report of record.
7. **Optional IDE spot-check** (skill §IDE spot-check) when an IDE is at hand.

## Exit criteria

- [ ] The audit ran in the right mode for the host, against a fresh build.
- [ ] Cleanup `ok`, with no residuals.
- [ ] Every non-pass step and finding is filed as a known issue, or is a `KNOWN` delta carrying its issue id.
- [ ] Authoritative only: the baseline and report were updated by the run itself, never by hand.
