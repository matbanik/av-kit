# av-kit Commands & Operational Reference

> Relocated from AGENTS.md (2026-06-13 instruction-set-optimization slim). Operational reference: Quick Commands, Skills index, MCP Servers, Context & Docs, RTK.
>
> Command lines below show tool argv only. Route and capture them through
> [`.agent/docs/output-evidence-policy.md`](output-evidence-policy.md) and
> terminal preflight before execution. RTK is required; see that policy.


## Quick Commands

> The following fenced block is an argv-only reference block. Route every selected
> argv through the canonical receipt policy before execution.

```bash
# Validation — select the scope from D6 registration below.
uv run pytest tests/ -x --tb=short -q
uv run pyright packages/
uv run ruff check packages/ tests/
npm --prefix ui run typecheck
npm --prefix ui run lint
npm --prefix ui run test
npm --prefix ui run build
npm --prefix mcp-server run typecheck
npm --prefix mcp-server run test
npm --prefix mcp-server run build

# MEU Status SSOT
uv run python tools/meu_status.py list --status pending --unblocked  # Next unblocked work
uv run python tools/meu_status.py next                              # Top 5 unblocked MEUs
uv run python tools/meu_status.py stats                             # Summary counts
uv run python tools/meu_status.py update <row_key> <status>         # Update status
uv run python tools/meu_status.py render --check                    # CI drift gate

# Execution-review frontmatter gate (first YAML block only)
uv run python tools/check_exec_review.py --self-test
uv run python tools/check_exec_review.py --review-file <rolling-exec-review.md> --expected-mode implementation --expected-target <plan>/implementation-plan.md --max-round 6

# Issue Triage (known-issues.yaml SSOT)
uv run python tools/issue_triage.py stats                            # Issue counts
uv run python tools/issue_triage.py list --json                      # All issues (machine)
uv run python tools/issue_triage.py list --severity critical         # Filter by severity
uv run python tools/issue_triage.py get <ISSUE-ID>                   # Single issue details
uv run python tools/issue_triage.py add --id <ID> --title <T> --severity <S> --component <C>  # Record new
uv run python tools/issue_triage.py verify                           # Flag stale (>30d)
uv run python tools/issue_triage.py verify --deep                    # Deep verify: file checks, test coverage
uv run python tools/issue_triage.py render                           # Regenerate markdown
uv run python tools/issue_triage.py bucket                           # Group issues into proposed MEU batches
uv run python tools/issue_triage.py triage                           # Generate triage-output.yaml
uv run python tools/issue_triage.py triage --output <PATH>           # Generate to custom path
uv run python tools/issue_triage.py discover --dry-run               # Scan for TODO/FIXME/HACK (preview)
uv run python tools/issue_triage.py discover                         # Scan and persist candidates
uv run python tools/issue_triage.py discover --root <DIR>            # Scan specific directory
uv run python tools/issue_triage.py promote <ID>                     # Promote candidate → open
uv run python tools/issue_triage.py dismiss <ID>                     # Dismiss candidate → dismissed
uv run python tools/issue_triage.py render --include-candidates      # Render with candidate section

# Development
pytest --cov=packages/core --cov-report=term            # Coverage (advisory)

# Run the Electron UI (PowerShell). The env line is REQUIRED in a VS Code / Cursor
# terminal - see the note below. There is no root package.json, so --prefix ui is
# not optional either.
$env:ELECTRON_RUN_AS_NODE=$null; npm --prefix ui run dev

# Runtime: build UI before real Electron tests.
$env:ELECTRON_RUN_AS_NODE=$null; npm --prefix ui run test:e2e
```

> [!IMPORTANT]
> **Clear `ELECTRON_RUN_AS_NODE` before ANY Electron launch — `npm run dev`, `npm run
> test:e2e`, or a packaged binary.** VS Code and Cursor set it to `1` in their integrated
> terminals (Process scope only; User and Machine are empty), which makes `electron.exe`
> start as a plain Node interpreter. The two symptoms look unrelated but share one cause:
>
> | Command | Symptom with the variable set |
> |---|---|
> | `npm --prefix ui run dev` | **Silent.** Main and preload build, `starting electron app...` prints, no window ever appears, nothing errors. |
> | `npm --prefix ui run test:e2e` | All 14 `_electron.launch()` sites die with `electron.exe: bad option: --remote-debugging-port=0`. |
>
> Check with `[Environment]::GetEnvironmentVariable('ELECTRON_RUN_AS_NODE','Process')`;
> confirm the fix with `npx electron --version` (Node's `v24.x` when set, Electron's
> `v42.x` when clear). A terminal opened outside the IDE never has it. Tracked as
> `E2E-ELECTRON-LAUNCH-FLAG` in `.agent/context/known-issues.md`.

> [!NOTE]
> **A stale packaged build is not a stale tree.** `ui/dist/win-unpacked/` is only refreshed
> by `npm --prefix ui run dist`; launching that binary shows whatever UI was current when it
> was last packaged, which is why source changes can appear to have no effect. `npm run dev`
> serves from source and always reflects the working tree. To tell them apart, grep the
> packaged bundle for a testid you expect: `grep -c queue-card ui/dist/win-unpacked/resources/app.asar`.


## Skills

| Skill | Path | Purpose |
|-------|------|---------|
| Git Workflow | `.agent/skills/git-workflow/SKILL.md` | Agent-safe git operations with SSH commit signing. Prevents interactive prompt hangs. |
| Codebase Quality Gate | `.agent/skills/quality-gate/SKILL.md` | Validation pipeline: type checks, linting, tests, anti-placeholder scans, evidence checks. Supports phase-level and MEU-scoped runs. |
| MEU Status SSOT | `.agent/skills/meu-status/SKILL.md` | Query, update, and render MEU completion status via the central YAML SSOT. Replaces manual edits to meu-registry.md and BUILD_PLAN.md status tables. |
| Pre-Handoff Review | `.agent/skills/pre-handoff-review/SKILL.md` | Self-review protocol addressing 10 recurring patterns from critical review analysis. Reduces average review passes from 4-11 to 3-5. |
| Terminal Pre-Flight | `.agent/skills/terminal-preflight/SKILL.md` | Mandatory pre-flight checklist for terminal commands. Enforces the redirect-to-file pattern to prevent PowerShell buffer saturation and session hangs. |
| Completion Pre-Flight | `.agent/skills/completion-preflight/SKILL.md` | Mandatory pre-flight checklist before stop/report events. Enforces task.md re-read gate and post-truncation recovery sequence to prevent premature stop. |
| Completion Timestamp | `.agent/skills/timestamp/SKILL.md` | Generate the canonical completion timestamp from the system clock using the skill's registered exact-receipt command; do NOT derive time from UTC tool response headers. |
| Issue Triage | `.agent/skills/issue-triage/SKILL.md` | Record, query, verify, and manage known issues via the YAML SSOT (`known-issues.yaml`). Use when discovering bugs or reviewing issue status. |
| Subagent Delegation | `.agent/skills/subagent-delegation/SKILL.md` | In-harness subagent detection + delegation gate (Cursor `.cursor/agents/`, Claude Code `.claude/agents/`). Resolves `fresh_worker`, routes eligible `task.md` rows to `av-kit-builder`/`av-kit-verifier`, and enforces the never-delegate categories. |
| CLI Dispatch | `.agent/skills/cli-dispatch/SKILL.md` | External CLI routing: Codex wrapper, Claude `-p`, agy `-p`. Independent review stays on the Codex chain. |
| Deep Research Prompting | `.agent/skills/deep-research-prompting/SKILL.md` | Portal-ready deep research prompt procedure: Pomera MCP preflight hard gate, provider capability recon query bank (Tavily/Exa routing), 14-day capability snapshots, D1/D2/D3 prompt templates, triangulation synthesis. Driven by `/inspiration-research`. |

## MCP Servers

| Server | Purpose | Verify With |
|--------|---------|-------------|
| `sequential-thinking` | Complex multi-step analysis | `sequentialthinking` |
| `user-pomera` | `/inspiration-research` search surface | `pomera_system` diagnose |
| `user-graphify` / `user-graphify-research` | Context-tool decision gate | `query_graph` |
| `user-headroom` | Context-tool decision gate | `headroom_stats` |
| av-kit `mcp-server/` | Product MCP | — |


## Context & Docs

- **How development works end-to-end** → `.agent/docs/development-lifecycle.md` — the 9-phase lifecycle (inspiration → committed code), human-intervention map, and infrastructure map. **Source of truth for the process.** Its narrative companion `.agent/docs/agentic-methodology.md` covers the *why* (philosophy, economics, design rationale). Read the lifecycle doc when onboarding to the workflow or when you need the full process map.
- **Cloud ↔ local collaboration** → `.agent/docs/cloud-local-collaboration.md` — who does what when the driver runs in the Linux cloud container and the target is Windows: `WINDOWS_GATE` exchange (request block, local pre-flight, result JSON, `windows-gate-check`, reopen rule), `ENV_BOUND_*` census, and the same split applied to issue-triage reproduction. Read at plan time for any project or triage pass that needs real Electron on Windows, NSIS, the login item or the capture picker.
- **Harness capability profiles** → `.agent/docs/harness-profiles.md` — capability flags (`role`, `plan_to_exec_gate`, `injects_auto_approval`, `can_dispatch_external_reviewer`, `native_shell`, `read_tool`/`shell_tool`/`end_turn_signal`) per harness, plus the tool-name substitution table. Read when a workflow/skill branches on harness identity or a tool name looks Antigravity-specific.
- **Human decision protocol** → `.agent/docs/human-decision-protocol.md` — precedent sweep → web research (`web_search_tool` ladder) → obviousness test → Decision Brief (recommendation first) or autonomous decision logged in the plan's Decision Log and the reflection's Decisions Log. **Read before presenting any question or decision to the human at any workflow stage.**
- **Model & CLI routing** → `.agent/docs/model-routing.md` — the routed stack (3 model tiers — Coordinator/Builder/Router — + external reviewer + 2 execution modes), the independent-reviewer chain, and nesting/delegation rules. Canonical source for "which model does which task."
- Testing strategy → `.agent/docs/testing-strategy.md`
- Code quality examples → `.agent/docs/code-quality.md`
- **Emerging standards** → `.agent/docs/emerging-standards.md` — living checklist of MCP/GUI/API standards discovered during development. **Read before planning any MCP or GUI MEU.**
- Role specs → `.agent/roles/`
- Handoff template → `.agent/context/handoffs/TEMPLATE.md`
- Current focus → `.agent/context/current-focus.md`
- Known issues → `.agent/context/known-issues.yaml` (SSOT) / `.agent/context/known-issues.md` (generated)
- Full specification → `docs/BUILD_PLAN.md`


<!-- headroom:rtk-instructions -->
# RTK (Rust Token Killer) - Token-Optimized Commands

Prefix shell commands with RTK. Native filters provide compact views only after
command-matrix verification. Unsupported commands and exact evidence use
`rtk proxy`; pass-through-looking forms are not assumed safe. (The originating
repo's `output-evidence-policy.md` is the longer form of this section; it is
deliberately not ported — see MANIFEST §EXCLUDED.)

## Key Commands

> The following fenced block is an argv-only reference block for RTK subcommands.
> It is not executable receipt guidance.

```bash
# Git (59-80% savings)
rtk git status          rtk git diff            rtk git log

# Files & Search (60-75% savings)
rtk ls <path>           rtk read <file>         rtk grep <pattern>
rtk find <pattern>      rtk diff <file>

# Test (90-99% savings) — shows failures only
rtk pytest tests/       rtk cargo test          rtk test <cmd>

# Build & Lint (80-90% savings) — shows errors only
rtk tsc                 rtk lint                rtk cargo build
rtk prettier --check    rtk mypy                rtk ruff check

# Analysis (70-90% savings)
rtk err <cmd>           rtk log <file>          rtk json <file>
rtk summary <cmd>       rtk deps                rtk env

# GitHub (26-87% savings)
rtk gh pr view <n>      rtk gh run list         rtk gh issue list

# Infrastructure (85% savings)
rtk docker ps           rtk kubectl get         rtk docker logs <c>

# Package managers (70-90% savings)
rtk pip list            rtk pnpm install        rtk npm run <script>
```

## Rules
- In command chains, classify each segment and preserve the first failing exit code.
- For debugging, document the bypass reason and retain the P0 receipt.
- `rtk proxy <cmd>` is the canonical unfiltered route for exact evidence.
- On Windows, use PowerShell 7 (`pwsh`) for child scripts that require modern cmdlets
  such as `Get-FileHash`; `powershell.exe` is legacy compatibility only.
<!-- /headroom:rtk-instructions -->


## D6 staged validation registration

Each row below defines argv, scope and stage. Common fields: cwd `P:/av-kit` (npm `--prefix` selects its package); blocking `yes`; expected exit `0` with actual diagnostics retained; shell `PowerShell`; receipt `C:/Temp/av-kit/D6-ID.txt`. Invoke each argv through `rtk proxy`, `*>` redirection, immediate `$code=$LASTEXITCODE`, receipt read and `exit $code`. Use distinct IDs for each run; do not overwrite final evidence with a later failed attempt. Publish decisive results as evidence.v1.

| D6 ID | Stage | Exact argv | Selected scope / prerequisite |
|---|---|---|---|
| py-types | static | `uv run pyright packages/` | Python product packages and shared Python config |
| py-lint | static | `uv run ruff check packages/ tests/` | Python product source/tests; targeted runs name touched files |
| py-tests | full | `uv run pytest tests/ -x --tb=short -q` | All product Python tests; targeted runs name affected test paths |
| ui-types | static | `npm --prefix ui run typecheck` | UI source/tests and tsconfig |
| ui-lint | static | `npm --prefix ui run lint` | UI source/tests, ESLint config |
| ui-tests | full | `npm --prefix ui run test` | UI Vitest suite and fixtures; pass affected paths for targeted checks |
| ui-build | full | `npm --prefix ui run build` | Electron main/preload/renderer outputs |
| ui-electron | runtime | `npm --prefix ui run test:e2e` | Real Electron; build first; clear process ELECTRON_RUN_AS_NODE; retain script's Playwright JSON output |
| mcp-types | static | `npm --prefix mcp-server run typecheck` | MCP source/tests and tsconfig |
| mcp-tests | full | `npm --prefix mcp-server run test` | MCP Vitest contracts and fixtures |
| mcp-build | full | `npm --prefix mcp-server run build` | MCP generated JS |
| mcp-audit | runtime | `npm --prefix mcp-server run audit -- --mode authoritative --baseline P:/av-kit/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json --report P:/av-kit/.agent/context/MCP/mcp-tool-audit-report.md --out C:/Temp/av-kit/D6-mcp-audit --agent <name>` | MEU-68 live audit (`.agent/workflows/mcp-audit.md`): Windows host, after `mcp-build` and `uv sync --frozen --all-packages`; spawns an isolated backend and drives `mcp-server/dist/index.js` over stdio. Exit 0 clean, 1 findings, 2 baseline refused, 3 isolation refused, 4 runner error. Recording or replacing the baseline adds `--update-baseline` (and `--no-baseline` the first time) per `BASELINE_UPDATE_RULE`. The Linux container runs `--mode container` only, which is never authoritative. |
| openapi | full | `uv run python tools/export_openapi.py --check openapi.committed.json` | API contract/export changes; inspect declared output diff |
| state-render | full | `uv run python tools/meu_status.py render --check` | SSOT/generated state consistency |
| task-contract | static | `uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task TASK` | Replace TASK with actual plan task path before execution |

No MCP lint script exists; do not invent one. Coverage remains advisory. Runtime display/dependency failures need actual errors and durable follow-up; no blanket sandbox exemption. Clear ELECTRON_RUN_AS_NODE before every Electron launch, including dev and packaged acceptance.

### Governance adoption gate

The active framework-update-adoption plan owns the exact V1–V24 commands and their staged dependencies. Its full scope is the adopted tooling, migration tests, wrapper fixtures, document contracts and protected-state checks; no product code/config is changed. Run V17/V18 static before V2–V13, V14 before review, and V15/V19 at the declared closeout stages. The test provider is fake for wrapper-contract, never live `all`.

### Input identity and evidence invalidation

Hash actual selected source/tests, shared fixtures/config, command manifest and relevant generated inputs; observe executable/runtime identity, installed dependency versions and relevant process environment (including registry selection and Electron flag) live before and after execution and on every reuse check. A saved environment description alone cannot prove freshness. A dirty worktree cannot be identified by HEAD alone. Any unknown input disables reuse. Static failure stops targeted/full, which are explicitly not_run; input changes require affected checks and a new fresh full gate before approval. The migration verifier's `stages` and `stage-state` recompute runtime identity and, when `task_path` is registered, the live task validation/dependency contract excluding administrative completion cells. They are not a universal product-runner substitute. Register other external inputs explicitly in the run's manifest.

Legacy `check_exec_review.py` remains for historical implementation-mode artifacts. New review-state/approved-state commands use execution mode and bind to an exact target, cap and ledger; a process exit 0 alone never approves work.
