# Framework update assessment

Observed 2026-09-26. This is a local-checkout comparison, not a remote freshness claim. No fetch, pull, implementation, commit or product tests were performed.

## Pinned inputs

- Framework: `P:/agentic-framework`, HEAD `003929c1cafa83359f0695415bbc06074a35f92e`; tracked working tree clean (`git status --short`, exit 0, empty status).
- av-kit: HEAD `a841d46308bcb58b6467d58db2d95175fe90fd91`, with extensive pre-existing tracked and untracked changes. The **working tree**, not HEAD alone, is the destination baseline.
- Last recorded adoption: `.agent/context/handoffs/2026-08-17-agentic-framework-adoption-handoff.md`. It records an August 17 copy but no source SHA. `e1bab7d` is the latest framework commit before that date, a historical comparison anchor, **not a proven exact installation base**.
- `git diff --stat e1bab7d..003929c`: 136 files changed, 24,921 insertions, 1,897 deletions (includes upstream's own artifacts).
- Tracked `core/` files compared after substituting `framework.vars` and mapping `templates/` to `.agent/templates/`: 130 files; 17 absent, 74 text differences, 38 equal, 1 binary. These are inventory results, not a request to copy 91 files. `upstream-inventory.json` lists every row. Other active template homes need semantic comparison too.

**Concurrent state observation:** a later read during this session found av-kit at `2e4c308` (`docs(agent): align planning and model routing guidance`), following `17230ca` (Phase 11 layout canon) and `0e4025e` (Capture cleanup). Existing dirty entries had become committed, and another session's `docs/execution/plans/2026-09-26-p11-queue-pages/` appeared. This planner did not commit or author those changes. AGENTS, GUARDRAILS, the legacy review checker and pyproject hashes still match the initial observations. The initial inventory remains a dated comparison; WP-0 must rebaseline at execution, never restore the old HEAD or discard concurrent work.

## Priority assessment

| Priority | Update / commits | av-kit evidence | Adoption decision |
|---|---|---|---|
| 1 | Runnable task/closeout gates and durable evidence; `5543d8c`, `5dbd65e`, `168cbc5` | Active TASK-TEMPLATE calls absent `tools/validate_closeout_artifacts.py`; task linter, shared evidence module and verification-principles doc also absent | Adopt the dependency-complete validator bundle and tests first. Bind new evidence to final input state; retain old review compatibility. |
| 1 | Staged adopter-owned checks; `168cbc5` | `PROJECT-PROFILE.md` D6 and `.agent/docs/commands.md` still describe a Python-only scaffold and future UI/MCP; both packages and actual scripts exist | Register current Python/UI/MCP commands, scope and invalidation policy. Preserve real Electron checks and the environment workaround. |
| 2 | Capability-class model resolution; `75ff2bd`, `06edd58`, `49ad5f0`, `ed04b70` | Wrapper has a hard-coded model default; active docs/templates have repeated pins. Shared `P:/.agent/model-registry.json` and resolver exist; repo has no registry overlay/catalog | Use the existing shared registry read-only with a repo-local overlay, explicit session selection and refusal tests. Never copy an empty template over the live registry. |
| 2 | Bounded review ledger, v2 verdicts, intent binding and human continuation; `5543d8c`, `ba4c920`, `59a42fb`, `5dbd65e` | No ledger, vocabulary, v2 schema, schema adapter or schema CLI; current `check_exec_review.py` only checks implementation review frontmatter | Adopt ledger + wrapper + schemas + normalization as one bundle after registry readiness. Preserve exact raw reviewer output, manual evidence and target binding. |
| 3 | Compact governance, authority clarification and rule-preservation map; `168cbc5`, `003929c` | AGENTS is 414 lines; GUARDRAILS 127. RTK required vs optional, stale scaffold descriptions and correction-loop stop conflicts coexist | Consolidate after supporting tools exist; keep av-kit domain, real GUI testing, human gates, profile overrides and stronger source-backed local controls. |
| Already present / preserve | Per-driver profiles, worker smoke history, task dependency/context columns, rolling reviews, issue/MEU tooling | Current modified governance files and August adoption record; Cursor fresh_worker remains none, Claude has separate smoke-backed setting | Selective merge only. No fresh bootstrap, seed replacement or worker activation. |
| Lower relevance / exclude | Generic first-adopter empty seeds, native macOS/Linux certification, optional hooks/snapshot systems, auto-commit helpers | Established Windows repo with populated state; upstream explicitly excludes optional M4 systems and native-platform certification | Not part of this adoption contract. No preflight.sh/agent-commit.sh adoption solely for inventory parity. |

## Material caveats and preserved decisions

1. Upstream rolling migration review has **Round 2 approved**, zero findings, at `.agent/context/handoffs/2026-09-26-governance-migration-implementation-critical-review.md`. Its approval explicitly excludes release readiness, native Linux/macOS and live loader/provider certification. The older `release-review.md` still says review required and mentions a protected planted pin. Do not reinterpret that checklist as current scoped verdict or certify a clean release; verify selected files independently. The same-vendor exception recorded there belongs to that loop and is **not transferable**.
2. Local docs currently prefer vendor diversity but permit independent separate-context review. Future upstream strict vendor-distinct routing will refuse Codex reviewing an OpenAI author. Keep Mat as the already-configured fallback, do not silently add providers or claim this planning review satisfies the future strict policy.
3. `tools/check_exec_review.py` accepts mode `implementation`; upstream closeout/schema tools use `execution`. Historical reviews must remain intact and checkable. The cutover requires explicit boundary translation or keeping the legacy checker for historical runs.
4. The current wrapper's Windows FullAccess recipe is an existing local policy for P0 receipt access; keep prompt-level write scope and record that it is not filesystem isolation.
5. Source-provided tools and portability helpers are code, not authority. Upstream text is adoption input; current user instructions govern this session. No new rule from upstream is silently activated by writing this plan.

## Re-derive observations

All commands ran through `rtk proxy`, all-stream redirection, immediate exit capture, receipt read and exit propagation. Durable decisive results are above; scratch paths below locate full logs, not sole proof.

| Command body | Exit | Observation / full receipt |
|---|---:|---|
| `git -C P:/agentic-framework log -25 --date=short --format='%h %ad %s'` | 0 | Latest `003929c` September 26; `C:/Temp/av-kit/adoption-framework-log.txt` |
| `git -C P:/agentic-framework status --short` | 0 | No tracked or ordinary untracked changes; `adoption-upstream-state.txt` |
| `git status --short` | 0 | Pre-existing governance/UI/spec/test work; `adoption-git-av.txt` |
| `python C:/Temp/av-kit/adoption_inventory.py` | 0 | 130 tracked core entries; inventory saved with this assessment |
| `rg -n ... tools/validate_closeout_artifacts.py` | 2 | `The system cannot find the file specified. (os error 2)`; absence independently checked in inventory |
| `codex login status` | 0 | `Logged in using ChatGPT`; no credential content read |
| `codex --version` | 0 | `codex-cli 0.157.0`, above local wrapper's 0.145.0 minimum |

Local source references: `PROJECT-PROFILE.md` Blocks A–F; `.agent/context/harness.local.md`; `.agent/docs/commands.md`; `ui/package.json`; `mcp-server/package.json`; `tools/check_exec_review.py`; current Phase 11 walkthrough and reflection. Source references are all under the pinned framework tree; no web freshness or remote branch claim is made.
