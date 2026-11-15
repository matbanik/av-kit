---
project: "2026-11-15-framework-small-syncs"
date: "2026-11-15"
source: "P:/agentic-framework commits 0a8d5bc (deep-research-prompting templates and strip script) and fb00d40 (commit_batch.py author_not_noreply / identity_env); grouping .agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md §3 Session 87"
meus: []
status: "draft"
template_version: "2.3"
---

# Implementation Plan: Deep-research templates and a commit-identity check

> **Project**: `2026-11-15-framework-small-syncs`
> **Build Plan Section(s)**: none (tooling, skill and workflow prose; no MEU)
> **Status**: `draft`

---

## Goal

**Goal anchor:** av-kit's `deep-research-prompting` skill carries upstream's prompt templates and image-strip script, adapted to this repository, and `agent-commit.ps1` refuses any commit whose author or committer address is not `219344396+matbanik@users.noreply.github.com`.

This is Session 87 of the 2026-11-15 grouping (§3, "the two remaining upstream features av-kit can use without new machinery"). It has two parts.

**Part 1: the deep-research port.** Upstream `P:/agentic-framework` commit `0a8d5bc` (2026-10-29) did three things:

- It moved the `/inspiration-research` orchestration into `core/.agent/skills/deep-research-prompting/SKILL.md` and cut the workflow to a stub.
- It added the provider templates (`templates/`).
- It added `scripts/strip_embedded_images.py`, which decodes the base64 figures a portal export embeds and repoints the links to image files.

av-kit has only an older `SKILL.md` (301 lines) and a 169-line orchestration workflow. The skill directory has not changed upstream since `0a8d5bc` (the upstream HEAD is `a73d6df`; the blob ids are in §Upstream blobs). Zorivest planned, ran and reviewed the same port (`P:/zorivest/docs/execution/plans/2026-10-29-deep-research-global-portal-refresh/`). Its review found two script defects, R1-F1 (filename collisions) and R1-F3 (titled definitions; empty or unhandled URIs). Both were fixed before upstream took the script, and AC-3 and AC-5 hold them fixed here.

**Part 2: the commit-identity check.** Mat's rule is that "a personal email address must never appear in a commit". Today the only guard is a manual H2-5 check in each task file (for example `docs/execution/plans/2026-11-14-capture-tool-flow/task.md:114`).

Upstream `fb00d40` (2026-11-12) added two refusals to `commit_batch.py`:

- `author_not_noreply` (`core/tools/commit_batch.py:226` and `:346` at `a73d6df`);
- `identity_env` (`:374`).

av-kit does not take `commit_batch.py`, its lanes or the standing grant (grouping D-825). This plan ports the two refusals as a standalone tool, and `agent-commit.ps1` (the git-workflow skill's commit script) calls it in both of its modes.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). Every payload is upstream text that must be ported byte for byte, a 379-line PowerShell script or a short new tool, all of which must be read verbatim; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host.
  - Validation goes through `rtk proxy`.
  - Receipts go under `C:/Temp/av-kit/fs/`, named `fs-*`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` does not apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `fs-plan-2026-11-15-framework-small-syncs` and `fs-execution-2026-11-15-framework-small-syncs`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor.
  - The fallback is Mat.
- **Queue:** this session runs after Sessions 84, 85 and 86 and after the post-rc.3 Session 83 (grouping D-824). None of them commit in between, so their changes are still uncommitted when this session starts. Execution waits for Mat's message (`plan_to_exec_gate: human`).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| Framework small syncs (no MEU) | `.agent/context/handoffs/2026-11-15-framework-small-syncs-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-framework-small-syncs-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-framework-small-syncs-implementation-critical-review.md`

The single non-MEU handoff follows `2026-11-05-closeout-register-grammar` and `2026-11-14-review-limits-no-token-budget`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `topic-row.txt`, `C:/Temp/av-kit/fs/base/`, `C:/Temp/av-kit/fs/upstream/` |
| WP-2 | Strip script: Red, then Green (rows 1 and 2) | WP-1 | shared | `tests/tooling/test_strip_embedded_images.py`, `scripts/strip_embedded_images.py` |
| WP-3 | Templates, SKILL and workflow stub (rows 3 and 4) | WP-2 | shared | `templates/`, `SKILL.md`, `inspiration-research.md`, `port-check.py` |
| WP-4 | Identity check: Red, then Green, then wiring (rows 5 to 8) | WP-1 | shared | `tools/check_commit_identity.py`, `tests/tooling/test_check_commit_identity.py`, `agent-commit.ps1`, git-workflow `SKILL.md`, `script-check.py` |
| WP-5 | Closeout (H1, H2) | WP-3, WP-4 | `compact_continue` | Handoff, review, reflection |

## User Review Required

> [!IMPORTANT]
> **`agent-commit.ps1` can now refuse a commit.** In both modes, it refuses when the author or committer address that git would use is not `219344396+matbanik@users.noreply.github.com`. It also refuses when `user.email` is a different address, and when an inherited `GIT_AUTHOR_EMAIL` or `GIT_COMMITTER_EMAIL` overrides that address.
>
> - The check runs before anything is staged.
> - It runs again on the new commit, before any push. If that second check fails, the commit already exists locally, so the script stops without pushing and Mat decides what to do with the commit.
> - The refusal names the reason (`author_not_noreply`, `committer_not_noreply`, `config_mismatch`, `identity_env:<VAR>`, `unconfigured`). It never prints an address, so a personal address cannot reach a receipt.
> - Your setup today passes; the live check is AC-20.
>
> **The check is exact.** It accepts only your noreply address, where upstream accepts any GitHub noreply address (D-884). A commit made with another person's noreply address is therefore refused.
>
> **Snapshots stay in `_inspiration/_capabilities/` (D-876, a brief accepted by your default ruling).** Upstream keeps them inside the skill folder, because its skill is shared by every project on the machine. av-kit's skill lives in this repository, and its three tracked snapshots already sit in `_inspiration/_capabilities/`.
>
> **`/inspiration-research` becomes a stub.** The orchestration steps move into the skill, as they did upstream and in Zorivest (D-877). Run `/inspiration-research <topic>` as before.
>
> **What this plan leaves out:**
>
> - `commit_batch.py`, lanes and the standing commit grant (grouping D-825);
> - upstream's secret scan;
> - refreshing the provider snapshots;
> - the separate `/deep-research` skill.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `SKILL_DIR` | `.agent/skills/deep-research-prompting/` |
| `WORKFLOW` | `.agent/workflows/inspiration-research.md` |
| `UPSTREAM(path)` | `git -C P:/agentic-framework show 0a8d5bc:core/.agent/skills/deep-research-prompting/<path>` (or `core/.agent/workflows/inspiration-research.md` for the stub). Row 0 saves each one to `C:/Temp/av-kit/fs/upstream/`, and its git blob id must equal §Upstream blobs. |
| `STRIP` | `SKILL_DIR/scripts/strip_embedded_images.py` |
| `CHECKER` | `tools/check_commit_identity.py` |
| `COMMIT_SCRIPT` | `.agent/skills/git-workflow/scripts/agent-commit.ps1` |
| `GIT_SKILL` | `.agent/skills/git-workflow/SKILL.md` |
| `EXPECTED_EMAIL` | `219344396+matbanik@users.noreply.github.com`, the one constant in `CHECKER`. It already appears in tracked files. |
| `BASE(path)` | The bytes of a file that already exists, copied by row 0 to `C:/Temp/av-kit/fs/base/`. These are the post-Session-86 bytes, not `HEAD` (D-887). |
| `ADAPTATIONS` | The table in §Adaptation table. `port-check.py` holds it as data. |
| `FORBIDDEN` | The case-insensitive regex `zorivest\|agentic-framework\|creative-writing\|P:/\|C:/Users\|machine-global\|every project\|@gmail\|this skill directory`. |
| `ROUTING_RE` | The census regex in `docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py` (`governance_inventory`): model names with version digits, `--class builder`, and `default reviewer: GPT`. |

### Upstream blobs

These are the git blob ids at `0a8d5bc`. They are unchanged at `a73d6df` (`git log` on the directory, 2026-11-15).

| Path under `core/.agent/` | Blob | Bytes | av-kit target | Treatment |
|---|---|---|---|---|
| `skills/deep-research-prompting/SKILL.md` | `234d25a` | 26816 | `SKILL_DIR/SKILL.md` (CRLF) | Rewrite to upstream plus `ADAPTATIONS` |
| `skills/deep-research-prompting/scripts/strip_embedded_images.py` | `4ef304e` | 7898 | `STRIP` (LF) | Byte-equal |
| `skills/deep-research-prompting/templates/d1-chatgpt.md` | `ef187b4` | 1805 | `SKILL_DIR/templates/d1-chatgpt.md` (LF) | Row A8 only |
| `skills/deep-research-prompting/templates/d2-gemini.md` | `e4c6c0d` | 1843 | `SKILL_DIR/templates/d2-gemini.md` (LF) | Row A8 only |
| `skills/deep-research-prompting/templates/d3-claude.md` | `24fff82` | 1825 | `SKILL_DIR/templates/d3-claude.md` (LF) | Row A8 only |
| `skills/deep-research-prompting/templates/domain-overlays/content-seo.md` | `30d2dde` | 7676 | same path under `SKILL_DIR` (LF) | Byte-equal, inert (D-879) |
| `skills/deep-research-prompting/templates/skeleton.md` | `cf92ba1` | 2407 | same path under `SKILL_DIR` (LF) | Byte-equal |
| `skills/deep-research-prompting/templates/snapshot.md` | `eef9dbe` | 1193 | same path under `SKILL_DIR` (LF) | Byte-equal |
| `workflows/inspiration-research.md` | `d9bf24f` | 783 | `WORKFLOW` (CRLF) | Stub, row W1 |

The upstream script and templates contain no `FORBIDDEN` match. The only hits are the line-6 `capabilities/` paths in d1, d2 and d3, which row A8 rewrites (plan-time scan, `C:/Temp/av-kit/s87/`). `Gmail` on d2-gemini line 14 is the product feature, which is why `FORBIDDEN` names `@gmail` and not `gmail`.

### Adaptation table

`port-check.py` builds the expected av-kit text from `UPSTREAM(path)` with CR removed. It applies these rows in order and compares the result with the av-kit file with CR removed. Line numbers are upstream's, in the CR-stripped `0a8d5bc` text. An upstream line not named here is carried over unchanged.

| Row | Where (upstream) | Upstream text | av-kit text | Why |
|---|---|---|---|---|
| A1 | SKILL L2 | `name: deep-research-prompting` | `name: Deep Research Prompting` | av-kit's existing name (D-878) |
| A2 | SKILL L3 | the last sentence of `description:`, `Includes the orchestration steps; a project supplies only its slash command and output root.` | `Includes the orchestration steps behind /inspiration-research, which writes to _inspiration/.` | The skill is repo-local |
| A3 | SKILL after L3 | — | `applies_to: [_inspiration/, .agent/workflows/inspiration-research.md]`, inserted | av-kit's existing line |
| A4 | SKILL L8–9 | `The machine-global procedure behind each project's deep-research command (default:` / `` `/inspiration-research`). `` followed by ``§1–§7 own …`` | ``The procedure behind the `/inspiration-research` command.`` followed by ``§1–§7 own …``, rewrapped into a single opening line | No other project exists here. L10–12 (the stub and `project_output_root` sentence) stay, because the stub still supplies that setting |
| A5 | SKILL L88 | `direct chat message from the human is.` | `direct chat message from the human is (GUARDRAILS.md SIGN 3).` | Local canon, `GUARDRAILS.md:33` |
| A6 | SKILL L158–159 | `shared across every topic and every project. One file per provider,` / `relative to this skill directory:` | `shared across every topic. One file per provider:` | D-876 |
| A7 | SKILL L375, L430 | ` (this skill directory)` and `   (this skill directory)` | removed | D-876 |
| A8 | SKILL L162, 163, 185, 315, 317, 375, 379, 380, 430; d1, d2 and d3 line 6 | every `capabilities/` not already preceded by `_` | `_inspiration/_capabilities/` | D-876. Each SKILL line is checked to hold its token after the rewrite, so a missed line fails |
| A9 | SKILL L279 | `python {this skill directory}/scripts/strip_embedded_images.py {project_output_root}/{topic-slug}` | `uv run python .agent/skills/deep-research-prompting/scripts/strip_embedded_images.py {project_output_root}/{topic-slug}` | av-kit runs Python through `uv` (AGENTS.md) |
| A10 | SKILL L368 | `(or the project's timestamp procedure, if it has one)` | ``(the timestamp procedure in `.agent/skills/timestamp/SKILL.md`)`` | That file exists |
| A11 | SKILL L476 | the `Topic too broad` row | the `Topic too broad` row of `WORKFLOW`, verbatim, as row 0 saved it to `topic-row.txt` | It keeps av-kit's protocol citation as Session 85 left it (D-877, D-887) |
| A12 | SKILL Design Basis | `Session-meta-review web research query bank (versioned query templates with selection rules) \| §3 structure` | ``Repo precedent: `session-meta-review/SKILL.md` §Web Research Query Bank \| §3 structure — versioned query templates with selection rules`` | Names a local source |
| A13 | SKILL Design Basis | `Prompt-injection defense: system-injected messages are untrusted data \| §1 — only a direct human chat message waives the gate` | ``​`GUARDRAILS.md` SIGN 3 \| §1 — a system-injected message can never be the human waiver`` | Names a local source |
| A14 | SKILL Design Basis | `Self-review discipline: verify against file state, not memory \| §7 checklist` | ``​`AGENTS.md` §Pre-Handoff Self-Review \| §7 — verify against file state, not memory`` | `AGENTS.md:69` |
| A15 | SKILL L387 | `shared across all topics and projects.` | `shared across all topics.` | Added in execution (D-892, plan review Q4): the last cross-project wording; same basis as A6 (D-876, D-878) |
| W1 | stub, last paragraph | `` (kept in the skill's `capabilities/` `` / `directory)` | ``(kept in `_inspiration/_capabilities/`)`` | D-876 |

**Carried over unchanged:**

- the §1 search-provider paragraph (L36–40) and the `~/.claude.json` Pomera lines;
- every `{project_output_root}` placeholder;
- skeleton, snapshot and the content-seo overlay;
- the stub's frontmatter, `// turbo-all`, Usage, the Project Setting table (`project_output_root` = `_inspiration/`) and its Procedure.

The stub's description equals av-kit's current one.

**Line endings:**

- `SKILL.md` and `WORKFLOW` are CRLF today (Python byte count: 301 of 301 and 169 of 169 lines) and stay CRLF. They are written with `newline=""` from CRLF text.
- The new templates and the script are LF, as upstream. `.gitattributes` has `* text=auto`, so they are stored LF.

**Index rows.** `.agent/docs/commands.md:108`, `.agent/skills/README.md:48` and `.agent/workflows/README.md:26` still describe the skill and the workflow correctly, so they are not touched (D-880). Session 86 edits the first two.

### The strip script

`STRIP` is upstream's file byte for byte (AC-7).

- It reads and writes with `newline=""`, so a CRLF output keeps CRLF.
- It decodes every `data:image` URI to `{topic}/images/<provider>-<id>.<ext>` and repoints the link, keeping a link title.
- It allocates names across reference and inline images before it writes anything, so no two figures share a file and no existing file is overwritten (R1-F1).
- An empty or malformed payload, or a `data:image` URI in a form it does not convert, leaves the file and the image folder unchanged and returns 1 (R1-F3).
- Exit codes: 0 when every file is clean; 1 on any failure; 2 on bad invocation or a missing directory. The optional second argument is the output glob (default `output-*.md`).

`tests/tooling/test_strip_embedded_images.py` (new, LF) ports the 18 tests of the global `P:/.agent/tests/test_strip_embedded_images.py`, which is read-only to this plan. The tests are renamed `test_ac_<n>_<upstream name>`. The file adds a CRLF case and runs its CLI cases through `uv run python` (D-881).

- Each test first asserts `STRIP.is_file()`, then loads it with `importlib` from a path constant. A missing script therefore fails by assertion, not by import error.
- Every address in the test file is a fixture such as `fixture@example.invalid`. The global test's author line is not copied.

### The identity checker

`CHECKER` is new, LF, standard library only, and runs with `uv run python tools/check_commit_identity.py [--repo PATH] [--commit REV] [--expected ADDRESS]`.

1. `git -C <repo> rev-parse --git-dir` must succeed; otherwise exit 2. `--repo` defaults to the current directory.
2. **Identity mode** (no `--commit`):
   - It reads `git var GIT_AUTHOR_IDENT` and `git var GIT_COMMITTER_IDENT`, which resolve exactly what `git commit` would record. That includes `user.email`, `author.email`, `committer.email`, the `GIT_AUTHOR_*` and `GIT_COMMITTER_*` variables, and `EMAIL` (git-config docs; plan-time probe in §Research References). The address is the text between `<` and `>`.
   - It also reads `git config --get user.email`.
   - It reports every reason that applies, one line each, in this order:
     - `identity_env:GIT_AUTHOR_EMAIL` / `identity_env:GIT_COMMITTER_EMAIL`: the variable is set and differs from the expected address (upstream `commit_identity_env`);
     - `author_not_noreply` / `committer_not_noreply`: the resolved address differs;
     - `config_mismatch`: `user.email` is set and differs;
     - `unconfigured`: `git var` exits non-zero, or `user.email` is unset.
3. **Commit mode** (`--commit REV`): `git show -s --format=%ae%x00%ce REV`. It uses `%ae`, not the mailmap-aware `%aE`, because the stored bytes are what GitHub reads. It reports `author_not_noreply` and `committer_not_noreply` the same way. A rev that does not resolve exits 2.
4. **Output and exit:**
   - `check_commit_identity: ok` and exit 0;
   - otherwise one line `check_commit_identity: refused <reason>` per reason, and exit 1;
   - usage errors exit 2 (argparse).
   - **The output never contains an observed address or any git stderr.** git's own message for a missing identity names the user and host (`user@HOST.(none)`), so stderr is captured and dropped. The only `@` the tool can print is none: no line it writes contains `@`.
5. `--expected` exists for tests only. `COMMIT_SCRIPT` never passes it (AC-19), so production always checks `EXPECTED_EMAIL`. Name variables are not checked, because only the address is the rule (upstream `commit_identity_env` comment).

### Wiring into `agent-commit.ps1` (D-883)

`COMMIT_SCRIPT` is CRLF (379 of 379 lines; `.gitattributes` `*.ps1 eol=crlf`) and stays CRLF. Every edit is add-only: each `BASE` line stays, in order (AC-19).

- **A helper, `Invoke-CommitIdentityCheck`,** goes after `Invoke-RtkGitExact`. It takes `-Repo`, plus optional `-Commit`, `-AuthorEmail` and `-CommitterEmail`.
  - It resolves the repo root as four levels above `$PSScriptRoot`.
  - When the email parameters are given, it saves and sets `GIT_AUTHOR_EMAIL` and `GIT_COMMITTER_EMAIL`.
  - It runs `uv run --no-sync --project <root> python <root>/tools/check_commit_identity.py --repo <Repo> [--commit <Commit>]`.
  - It restores the variables in `finally` and returns the exit code.
  - A missing `uv` or any non-zero exit counts as a refusal, so it fails closed.
- **Legacy mode:**
  - At the end of Step 1, before the Step 2 header, it calls the helper with the current directory. On a non-zero exit it prints `ERROR: commit identity refused (see the lines above)` and exits 1. Nothing has been staged yet: `git add -A` is Step 3.
  - After `Committed successfully` and before Step 6, it calls the helper with `-Commit HEAD`. On a non-zero exit it prints that the local commit carries a refused identity, that nothing was pushed, and that the commit is left for the human. It exits 1.
  - The `[n/7]` step labels do not change.
- **Exact-scope mode:**
  - After the message-hash check and before the `commit.gpgsign` read, it calls the helper with `-Repo $repo -AuthorEmail $descriptor.author_email -CommitterEmail $descriptor.author_email`. Those are the values the commit block sets later. A non-zero exit throws `Exact-scope commit identity refused`.
  - After `verify-commit`, it calls the helper with `-Commit $actualSha`. A non-zero exit throws.
- **`GIT_SKILL`** (CRLF, 283 lines, add-only):
  - Under `### What the Script Does`, after item 2, a line: ``2b. ✅ Refuses an author or committer address other than the noreply address (`tools/check_commit_identity.py`), before staging and again before the push``.
  - Under `### Exact-Scope Signed Commit Mode`, one sentence saying that the descriptor's `author_email` is checked the same way before signing.
  - In the Agent Workflow Checklist, a line after Step 1: ``- [ ] Step 1b: Identity — `uv run python tools/check_commit_identity.py` must print `ok` ``.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `CHECKER` argv | `argparse` in `CHECKER` | `--repo` an existing git work tree; `--commit` a rev that resolves; `--expected` a non-empty string | An unknown flag exits 2. A non-repo path or bad rev exits 2 with a one-line message that holds no address. |
| `COMMIT_SCRIPT` content descriptor | `Invoke-ExactScopeCommit` | `author_email` is now also checked by `CHECKER` | Unchanged: other fields are ignored, as today |
| `STRIP` argv | `STRIP` `main` | `<topic-dir>` exists; optional glob | More arguments exit 2 (upstream) |

### Acceptance Criteria

Tests are named `test_ac_<n>_…`.

- **AC-1 to AC-6** are in `tests/tooling/test_strip_embedded_images.py`.
- **AC-11 to AC-18** are in `tests/tooling/test_check_commit_identity.py`. Each test builds a temp repo and runs `git` and `CHECKER` with an environment built from scratch:
  - `GIT_CONFIG_GLOBAL` points to a temp file;
  - `GIT_CONFIG_NOSYSTEM=1`;
  - `EMAIL`, `GIT_AUTHOR_*` and `GIT_COMMITTER_*` are removed unless the case sets them.
  - The fixture addresses are synthetic: `100+fixture@users.noreply.github.com` (passed as `--expected`), `200+other@users.noreply.github.com` and `fixture@example.invalid`.
- **AC-7 to AC-10, AC-19 and AC-20** are plan-local checks, because they read `P:/agentic-framework` or the live repository, which CI does not have.

Every `CHECKER` test also asserts that stdout and stderr together contain no `@`.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-1 | unit | `STRIP` decodes reference definitions (with and without angle brackets) and inline images to `images/<provider>-<id>.<ext>`. Each written file's bytes equal the decoded payload, and the link points to that file. `image/svg+xml` maps to `.svg`. | Spec (`0a8d5bc` script; global tests 1–4) | No `data:image` remains in the output; a test that finds one fails |
| AC-2 | unit | A second run changes nothing, and a file with no images keeps its bytes | Spec (global tests 5–6) | The second run's bytes and image list equal the first run's |
| AC-3 | unit | Two figures never share a file: a reference `inline1` against the first inline image, labels that normalise alike (`fig 1`, `fig-1`), and an existing `images/` file that is not overwritten. Every original image survives with its own bytes. | Spec (Zorivest R1-F1, fixed upstream) | Two different PNG payloads; the test fails if either payload is missing from `images/` |
| AC-4 | unit | A title on a reference definition or an inline image, and braces in alt text and labels, survive the rewrite | Spec (Zorivest R1-F3; global tests 11–13) | A rewrite that drops the title fails the exact-text comparison |
| AC-5 | unit | A malformed payload, an empty payload (parametrized) or an unhandled `data:image` form makes `STRIP` fail and leaves the file bytes and the `images/` folder unchanged, even when a valid image sits in the same file | Spec (Zorivest R1-F3) | A valid image next to a bad one is the negative: no image is written |
| AC-6 | integration | `uv run python STRIP <topic> [glob]` as a subprocess: it strips every `output-*.md`, a glob selects other names, the exits are 0, 1 and 2 (no args, a missing dir, a bad file), and a CRLF output keeps CRLF after the rewrite. Entrypoint: the command named in SKILL §6. | Spec (global tests 16–18); Local Canon (A9, `newline=""`) | A CRLF file that comes back with LF fails a byte count |
| AC-7 | unit | `port-check.py --files`: `STRIP`, skeleton, snapshot and content-seo equal `UPSTREAM` byte for byte; d1, d2 and d3 equal `UPSTREAM` after row A8 only. Each saved upstream file's blob id equals §Upstream blobs. | Spec (`0a8d5bc`) | `--selftest`: a template with one extra word, and an upstream copy with a wrong blob id, are both refused |
| AC-8 | unit | `port-check.py --skill`: `SKILL.md` and `WORKFLOW` equal `UPSTREAM` after `ADAPTATIONS` (CR removed on both sides). Both are CRLF on every line. Row A11 equals `topic-row.txt`. Every row of the table matched at least once. | Local Canon (D-876 to D-878) | `--selftest`: a SKILL with one adaptation left out, one with an LF line, and an adaptation row that matches nothing are each refused |
| AC-9 | unit | `port-check.py --lint`: no ported file matches `FORBIDDEN`. Every `capabilities/` path in them reads `_inspiration/_capabilities/`. Every relative Markdown link in `SKILL.md` and the templates resolves (targets that are `...`, `{…}`, `http…` or bare `#` anchors are skipped, except `#orchestration`, which must match a heading). No added or changed line matches `ROUTING_RE`, except d2-gemini line 11 (`Gemini 4 Argon`, upstream text, not in the adoption manifest). | Local Canon (session brief; `verify_adoption.py` census) | `--selftest`: a line with `P:/agentic-framework`, a bare `capabilities/chatgpt.md`, a broken link and a `gpt-5` line are each refused |
| AC-10 | integration | The adoption tests that copy the live `SKILL.md`, `WORKFLOW`, `GIT_SKILL` and `COMMIT_SCRIPT` into a migrated tree still pass: `pytest tests/tooling/test_framework_adoption.py` | Local Canon (`test_framework_adoption.py` `migrated_tree`) | The governance static-oracle case is in that file; a routing line added to `GIT_SKILL` fails it |
| AC-11 | integration | `CHECKER` in a repo whose `user.email` is the expected address exits 0 and prints `check_commit_identity: ok`. With `user.email` set to another address it exits 1 and prints `author_not_noreply`, `committer_not_noreply` and `config_mismatch`. | Spec (`fb00d40` `check_identity`); Human-approved (Mat's identity rule) | Output holds no `@` and neither fixture address |
| AC-12 | integration | With a good config: `GIT_AUTHOR_EMAIL` set to another address gives `identity_env:GIT_AUTHOR_EMAIL` and `author_not_noreply`, but not `committer_not_noreply`; `GIT_COMMITTER_EMAIL` gives the mirror image; `GIT_AUTHOR_NAME` alone gives `ok`. With a bad config, both email variables set to the expected address still give `config_mismatch`. | Spec (`fb00d40` `commit_identity_env`) | The name-only case is the negative that must pass |
| AC-13 | integration | `author.email` set to another address gives only `author_not_noreply`; `committer.email` gives only `committer_not_noreply`. `EMAIL` set to another address with `user.email` unset gives `unconfigured` with both `*_not_noreply`; with `user.email` set, `EMAIL` is ignored and the result is `ok`. | Research-backed (git-config docs; plan-time probe) | Each case asserts the exact set of reason lines, so an extra or a missing one fails |
| AC-14 | integration | No identity at all (no `user.email`, no `EMAIL`) exits 1 with `unconfigured`, and the output holds neither `(none)` nor the host name | Research-backed (git prints `user@HOST.(none)`) | `socket.gethostname()` must not appear in the output |
| AC-15 | integration | An unknown flag, a `--repo` that is not a git work tree, and a `--commit` rev that does not resolve each exit 2, with no traceback | Local Canon (exit-code convention, `STRIP`) | `Traceback` must not appear in the output |
| AC-16 | integration | `--commit REV`: a commit made with the expected address exits 0; one with another author gives `author_not_noreply`; one with only another committer gives `committer_not_noreply`; a `.mailmap` that maps the other address to the expected one does not hide it | Research-backed (GitHub push protection checks author and committer) | The mailmap case is the negative |
| AC-17 | integration | `pwsh -NoProfile -File COMMIT_SCRIPT -Message "test: fixture" -SkipTests -NoPush`, with its working directory in a temp repo: (a) `user.email` set to another address exits 1, `HEAD` is unchanged and the fixture file is still untracked; (b) `user.email` set to `EXPECTED_EMAIL`, read from the loaded `CHECKER` module, exits 0, and the new commit's `%ae` and `%ce` equal it; (c) the good config with `GIT_COMMITTER_EMAIL` set to another address exits 1 with `HEAD` unchanged | Human-approved (D-883) | (a) and (c) are the negatives. The test fails if `HEAD` moved |
| AC-18 | integration | Exact-scope mode with a valid manifest, base, message hash and descriptor whose `author_email` is `fixture@example.invalid` exits non-zero, prints `author_not_noreply` and leaves `HEAD` unchanged, before the signing check runs (no `SSH commit-signing` text in the output). Skipped when `rtk` is absent, as on CI. The session gate refuses that skip. | Human-approved (D-883) | In Red, the script reaches the signing check instead, which fails the `author_not_noreply` assertion |
| AC-19 | unit | `script-check.py`: `COMMIT_SCRIPT` and `GIT_SKILL` are add-only against `BASE` and CRLF on every line. In `COMMIT_SCRIPT`, the legacy pre-commit call comes before `git add -A`, the post-commit call before `git push`, the exact-scope early call before `commit.gpgsign`, and the late call after `verify-commit`. `--expected` does not appear. `GIT_SKILL` names `tools/check_commit_identity.py` under What the Script Does and in the checklist. | Local Canon (D-883, D-887) | `--selftest`: a copy with a removed `BASE` line, one with an LF line, one with the pre-commit call moved after `git add -A`, and one passing `--expected` are each refused |
| AC-20 | integration | Live: `uv run python tools/check_commit_identity.py` in `P:/av-kit` exits 0, and the same with `--expected 100+fixture@users.noreply.github.com` exits 1, so the live pass is not vacuous | Human-approved (Mat's identity rule) | The `--expected` run is the negative |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| What the strip script does | Spec | Upstream's file, byte for byte |
| Where the snapshots live | Human-approved | D-876 (brief, default accepted) |
| How the SKILL text changes for av-kit | Local Canon | D-877, D-878, the adaptation table |
| Which addresses pass | Human-approved | D-884: Mat's rule names one address |
| Which inputs decide the address | Research-backed | git-config docs and the plan-time probe: `git var` resolves them all |
| Where the check runs | Human-approved | D-883 (brief, default accepted) |
| Upstream text that Session 85 changes in `WORKFLOW` | Local Canon | D-887: bind to the post-85 bytes; S2 if Session 85 changed anything other than the `Topic too broad` row |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `.agent/skills/deep-research-prompting/SKILL.md` | modify | Rewritten to upstream plus `ADAPTATIONS`; stays CRLF |
| `.agent/skills/deep-research-prompting/scripts/strip_embedded_images.py` | new | Byte-equal to upstream |
| `.agent/skills/deep-research-prompting/templates/d1-chatgpt.md`, `d2-gemini.md`, `d3-claude.md` | new | Upstream plus row A8 |
| `.agent/skills/deep-research-prompting/templates/skeleton.md`, `snapshot.md`, `domain-overlays/content-seo.md` | new | Byte-equal to upstream |
| `.agent/workflows/inspiration-research.md` | modify | The upstream stub plus row W1; stays CRLF |
| `tests/tooling/test_strip_embedded_images.py` | new | AC-1 to AC-6 |
| `tools/check_commit_identity.py` | new | The checker |
| `tests/tooling/test_check_commit_identity.py` | new | AC-11 to AC-18 |
| `.agent/skills/git-workflow/scripts/agent-commit.ps1` | modify | The helper and four calls, add-only; stays CRLF |
| `.agent/skills/git-workflow/SKILL.md` | modify | Three add-only lines; stays CRLF |

### Project files

- **Plan-local scripts**, all in this plan folder: `baseline.ps1`, `red-check.py`, `identity.py`, `port-check.py`, `script-check.py`, `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `topic-row.txt`.
- **State:** `docs/execution/metrics.md`, `.agent/context/current-focus.md`, the handoff, the rolling reviews and the reflection.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| `commit_batch.py`, lanes, the governed land, the standing commit grant and the commit-gate hook | out-of-scope | — | Grouping D-825 and §3 "Not grouped" (`.agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:196`, `:129-131`) |
| Upstream's secret scan (`fb00d40`) | out-of-scope | — | Grouping §3 Session 87 names only the identity check (`:118`); D-886 |
| Refreshing the three provider snapshots under `_inspiration/_capabilities/` | out-of-scope | — | Snapshot refresh is a run of `/inspiration-research` (SKILL §4 TTL), not part of the port; D-886 |
| The machine-global copy under `P:/.agent/skills/deep-research-prompting/` and its test | out-of-scope | — | That copy is outside the repo (session brief hard constraint); D-886 |
| The separate `/deep-research` skill (`.agent/skills/deep-research/`, `.agent/workflows/deep-research.md`, `.agent/workflows/prompts/deep-research/`) | out-of-scope | — | `PROJECT-PROFILE.md:104` keeps it alongside `/inspiration-research`; D-886 |
| `.agent/docs/commands.md`, `.agent/skills/README.md`, `.agent/workflows/README.md` | out-of-scope | — | Their rows stay accurate (D-880); Session 86 edits the first two |
| The manual author check in the task template's H2-5 row | out-of-scope | — | Template wording belongs to Sessions 84 and 85 (grouping §3 `:73-100`); D-886 |

## BUILD_PLAN.md Audit

This project adds no build-plan section and changes no MEU, so `docs/BUILD_PLAN.md` and `meu-status.yaml` do not change. The unrelated triage workstream may have uncommitted edits in them, and this session leaves those alone. H1-3 proves the render is consistent:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/fs/fs-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/fs/fs-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. **Tree state.** It records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`. Sessions 84 to 86 and the triage workstream are expected there.
2. **Path-scoped baseline.**
   - It writes `baseline-scope.json`: for each path in §Files Modified, its SHA-256, or `absent`.
   - Every new file must be `absent`.
   - It writes `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope (or `deleted`). S4 and `scope-paths` compare against it.
   - It copies the four existing files (`SKILL.md`, `WORKFLOW`, `GIT_SKILL`, `COMMIT_SCRIPT`) to `C:/Temp/av-kit/fs/base/` as `BASE`.
3. **Session 85 binding (D-887).**
   - `SKILL_DIR/SKILL.md` must equal `git show HEAD:` that path. Session 85 is not expected to edit it.
   - `git diff HEAD -- WORKFLOW` may change only the `Topic too broad` row. Any other changed line is S2.
   - It writes that row, as `WORKFLOW` holds it now, to `topic-row.txt`.
4. **Upstream copies.** It saves each `UPSTREAM(path)` to `C:/Temp/av-kit/fs/upstream/` and checks each blob id with `git hash-object` against §Upstream blobs.
5. **Base receipts.** It runs `uv sync --frozen --all-packages` and the base Python suite (`fs-base-py.txt`), with `TMP` and `TEMP` at `C:\Temp\av-kit\fs\tmp`.
6. **Plan-local scripts.**
   - It copies `red-check.py` and `identity.py` from `2026-11-05-closeout-register-grammar`, with this plan's `PLAN` and `PROJECT_ARTIFACTS`, and with `DECLARED_NEW` left at the selftest names.
   - It writes `port-check.py` and `script-check.py` per AC-7 to AC-9 and AC-19.
   - It runs the four selftests. The `port-check.py` and `script-check.py` selftests use their own fixtures, not the repo files.

If any step fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require test_ac_<n>` checks that exactly.
- **New code fails by assertion.** Each test asserts that `STRIP` or `CHECKER` is a file before it loads it, so a missing file prints an assertion, not an import error.
- **Rows 1 and 5** require every AC in their file.
  - AC-17(b) fails in Red because `CHECKER`, which supplies `EXPECTED_EMAIL`, is missing.
  - AC-18 fails in Red because the script reaches the signing check instead. `rtk` is on the driver's PATH, so it runs.
- **Expectations stay immutable in Green.**
- **Line endings.** `COMMIT_SCRIPT`, `GIT_SKILL`, `SKILL.md` and `WORKFLOW` keep CRLF. They are measured with Python bytes and written with `newline=""`.

### 3. Port checks (rows 3 and 4)

- **`port-check.py`** holds §Upstream blobs and §Adaptation table as data and reads the saved upstream copies.
  - `--files` checks AC-7, `--skill` checks AC-8 and `--lint` checks AC-9. With no flag, it runs all three.
  - It reads every file as bytes.
- **AC-10** runs the adoption test file, because its migrated tree copies the live bytes of `SKILL.md`, `WORKFLOW`, `GIT_SKILL` and `COMMIT_SCRIPT`.

### 4. Live check (row 8)

AC-20 runs `CHECKER` in `P:/av-kit` with the driver's real environment. It runs once with no flag and once with `--expected` set to the synthetic address. Neither output can hold an address.

### Session gate (H1-2)

`session-gate.ps1` follows the peer's shape:

- one receipt per step in `C:/Temp/av-kit/fs/`, named `fs-D6-<step>`;
- fail-fast, with later steps printed as `not_run`;
- the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `tools-lint` (`ruff check tools/check_commit_identity.py tests/tooling/ .agent/skills/deep-research-prompting/scripts/`); `py-lint` (`ruff check packages/ tests/`); `task-contract`; `scope-paths` (every changed path is in §Files Modified, in this plan folder, in the closeout artifacts or in `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps its row-0 content state); `port-check`; `script-check`; `red-check-selftest` |
| Targeted | `strip-tests` and `identity-tests`: `pytest` on the two new files with `-rs`. The step fails if the receipt shows any skip, so AC-18 must run. `adoption-tests`: `pytest tests/tooling/test_framework_adoption.py` |
| Fresh full | `py-tests` (the full suite); `state-render`; `closeout-selftest`; `identity-live` (AC-20) |
| Skipped, with reason | `py-types`: `pyright packages/`, and nothing under `packages/` changes. `ui-*`: nothing under `ui/` changes. `mcp-*`: no MCP change. `openapi`: no `packages/api` change (H1-4). `build-record`: no build |

`py-tests` excuses only ids that row 0's receipt shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a changed line in `WORKFLOW` other than the `Topic too broad` row, or a change to `SKILL_DIR/SKILL.md` since `HEAD`, or `GIT_SKILL` without the anchors that §Wiring names | Stop. An earlier session changed text this port replaces; bring the diff and the options to Mat |
| S3 | A Red receipt fails `red-check.py` | Fix the test setup; do not move to Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path changes content during the session | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An upstream blob id differs from §Upstream blobs | Stop; upstream moved, and the port must be re-planned |
| S6 | AC-20 fails on the live repository | Stop. The local identity is wrong, and only Mat may change git configuration (CLAUDE.md "Do not change it") |
| S7 | Codex is unavailable or the ledger refuses | Mat |

## Decision Log

> [!WARNING]
> D-876 and D-883 failed the obviousness test, so each is written below as a Decision Brief. Mat's standing ruling of 2026-11-15 accepts each brief's recommendation, so each is recorded `resolution: human` and `Human-approved`. That ruling does not cover commit, push, merge, release, destructive data operations, external disclosure or credentials, and none of those arises here. Every other row is autonomous, with its source. The `grouping` rows are carried from the grouping's §8.

```yaml
decision_log:
  - id: D-818
    stage: grouping
    question: "Group the HDP enhancements and the other upstream features for av-kit?"
    resolution: human
    class: product-preference
    chosen: "Yes. Four sessions, 84 to 87; no plan created."
    source_tag: Human-approved
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:190 — the grouping row"]
    research: { engine: none, sources: [] }
    reasoning: "Mat asked for exactly this."
    human_message_reference: "USER_EXPLICIT 2026-11-15 \"Look at P:/zorivest and P:/agentic-framework. I'd like to create new session grouping for enhacments to HDP so I do not have to make expert decsions and other features that have been introduced.\""
  - id: D-819
    stage: grouping
    question: "Which upstream features are grouped?"
    resolution: autonomous
    class: two-way
    chosen: "The HDP port, the closeout fix, the deep-research templates and the identity check. The rest are in §3 Not grouped, each with its reason."
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:191 — the grouping row"]
    research: { engine: none, sources: [] }
    reasoning: "Lanes conflict with Mat's main-only rule. Credits, the stop gate and dispatch resume serve headless runs av-kit does not have. Porting everything lost: most of it adds machinery av-kit has no use for."
  - id: D-821
    stage: grouping
    question: "How is the work sliced?"
    resolution: autonomous
    class: two-way
    chosen: "Four sessions with no MEU: validator first, then the protocol, then the expert pass and hand-over, then the small syncs."
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:193 — the grouping row"]
    research: { engine: none, sources: [] }
    reasoning: "Framework ports run without an MEU (Session 49b, D-280; review-limits-no-token-budget)."
  - id: D-824
    stage: grouping
    question: "Where do Sessions 84 to 87 sit in the queue?"
    resolution: autonomous
    class: two-way
    chosen: "After Session 74: 84, 85 and 86 ahead of the post-rc.3 Sessions 75 to 83; 87 after 83."
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:196 — the grouping row"]
    research: { engine: none, sources: [] }
    reasoning: "The post-rc.3 sessions are P2 to P4 debt with no deadline; this session is P3 and independent."
  - id: D-825
    stage: grouping
    question: "Port the standing commit grant and the commit-gate hook?"
    resolution: autonomous
    class: two-way
    chosen: "No, not now. Today's rule stays: commits happen on Mat's word."
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:197 — the grouping row"]
    research: { engine: none, sources: [] }
    reasoning: "Adopting the grant edits AGENTS.md 'Never auto-commit/push', an M-3 item only Mat can rule, and it needs run parameters (D-733). This plan's identity check adds a refusal and grants nothing."
  - id: D-875
    stage: planning
    question: "What does the deep-research port carry?"
    resolution: autonomous
    class: two-way
    chosen: "The SKILL rewrite to upstream 0a8d5bc, the six templates, the strip script, and the workflow cut to upstream's stub"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:117 — templates and strip_embedded_images.py", "P:/zorivest/docs/execution/plans/2026-10-29-deep-research-global-portal-refresh/implementation-plan.md:339 — D-1, the SKILL absorbs the orchestration"]
    research: { engine: none, sources: [] }
    reasoning: "The templates and the SKILL refer to each other (§5 points at templates/, §6 runs the script), so porting the templates without the SKILL would leave the SKILL describing inline templates that no longer match. Porting only the templates lost for that reason."
  - id: D-876
    stage: planning
    question: "Where do the provider capability snapshots live after the port?"
    resolution: human
    class: source-conflict
    chosen: "A: keep _inspiration/_capabilities/, with raw dumps in a dated subfolder of _inspiration/_capabilities/sources/"
    source_tag: Human-approved
    precedents: [".agent/skills/deep-research-prompting/SKILL.md (av-kit, today) — snapshots in _inspiration/_capabilities/", "PROJECT-PROFILE.md:103 — _inspiration/ is Keep", "P:/zorivest/docs/execution/plans/2026-10-29-deep-research-global-portal-refresh/implementation-plan.md:350 — D-2, committed under the skill's capabilities/ because the skill became machine-global"]
    research: { engine: tavily, sources: ["https://www.agensi.io/learn/where-are-claude-skills-stored — project skills live in the repo; bundled reference files sit in the skill folder", "https://joseparreogarcia.substack.com/p/claude-code-skills-explained — skill folders hold instructions and supporting files"] }
    reasoning: "Upstream moved the snapshots into the skill because one global skill serves every project. av-kit's skill is repo-local, the three tracked snapshots already sit in _inspiration/_capabilities/, and moving them would churn tracked files for no reader. Mat's standing ruling accepts the recommendation."
    human_message_reference: "USER_EXPLICIT 2026-11-15 \"Run HDP on any decisions that come up and and I approving acceptance of the defaults.\""
  - id: D-877
    stage: planning
    question: "Where does the orchestration live, and which Topic too broad row survives?"
    resolution: autonomous
    class: two-way
    chosen: "In the SKILL's §Orchestration, as upstream; the workflow becomes the stub; the Topic too broad row is av-kit's own, as Session 85 left it"
    source_tag: Local Canon
    precedents: ["P:/zorivest/docs/execution/plans/2026-10-29-deep-research-global-portal-refresh/implementation-plan.md:339 — D-1", ".agent/workflows/inspiration-research.md:158 — av-kit's row cites human-decision-protocol.md"]
    research: { engine: none, sources: [] }
    reasoning: "Upstream's row says 'the project's human-decision procedure, if it has one'; av-kit has one, and its row names it. Keeping two copies of the orchestration lost: they would drift."
  - id: D-878
    stage: planning
    question: "How is the upstream text adapted to av-kit?"
    resolution: autonomous
    class: two-way
    chosen: "Rows A1 to A14 and W1 of the adaptation table: no other project, no machine-global wording, no home path, local sources named in the Design Basis"
    source_tag: Local Canon
    precedents: ["session brief — adapt, no other project names, no home paths", "GUARDRAILS.md:33 — SIGN 3", "AGENTS.md:69 — §Pre-Handoff Self-Review"]
    research: { engine: none, sources: [] }
    reasoning: "Each row replaces text that only makes sense for a machine-global skill. Everything else is carried byte for byte, so a later upstream sync is a diff against a known table."
  - id: D-879
    stage: planning
    question: "Port the content-seo domain overlay?"
    resolution: autonomous
    class: two-way
    chosen: "Yes, byte-equal and inert; av-kit's stub names no overlay"
    source_tag: Local Canon
    precedents: ["upstream SKILL §5 Domain overlays — an overlay applies only when a stub names it"]
    research: { engine: none, sources: [] }
    reasoning: "The SKILL's §5 lists it, so leaving it out would leave a dangling reference. It has no effect until a stub names it."
  - id: D-880
    stage: planning
    question: "Do the index rows for the skill and workflow change?"
    resolution: autonomous
    class: two-way
    chosen: "No; commands.md:108, skills/README.md:48 and workflows/README.md:26 stay as they are"
    source_tag: Local Canon
    precedents: [".agent/docs/commands.md:108 — names the gate, recon, snapshots, D1/D2/D3 and /inspiration-research, all still true"]
    research: { engine: none, sources: [] }
    reasoning: "Each row is still accurate, and Session 86 edits two of those files. Not touching them avoids a sibling overlap."
  - id: D-881
    stage: planning
    question: "Where does the strip script's test live, and what does it cover?"
    resolution: autonomous
    class: two-way
    chosen: "tests/tooling/test_strip_embedded_images.py: the 18 global tests renamed test_ac_N_… (N the AC number), plus a CRLF case, with the CLI cases run through uv run python"
    source_tag: Local Canon
    precedents: ["pyproject.toml:28 — testpaths is tests", "tests/tooling/test_review_limits.py — a tooling test loaded by path", "P:/.agent/tests/test_strip_embedded_images.py — the global tests"]
    research: { engine: none, sources: [] }
    reasoning: "CI runs tests/ only, so a test beside the skill would never run. The CRLF case covers av-kit's Windows outputs."
  - id: D-882
    stage: planning
    question: "What does the identity checker check, and how?"
    resolution: autonomous
    class: two-way
    chosen: "tools/check_commit_identity.py: git var for the resolved author and committer, git config user.email, the two email variables, and --commit for a made commit (%ae/%ce); reasons, never addresses"
    source_tag: Research-backed
    precedents: ["P:/agentic-framework core/tools/commit_batch.py:226,346,374 (a73d6df) — author_not_noreply, config_mismatch, unconfigured, identity_env", "docs/execution/plans/2026-11-14-capture-tool-flow/task.md:114 — today's manual author check"]
    research: { engine: tavily, sources: ["https://git-scm.com/docs/git-config — GIT_AUTHOR_*/GIT_COMMITTER_* and EMAIL override user.*, author.* and committer.*", "https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables — the email variables set the recorded fields", "https://github.com/orgs/community/discussions/177282 — GitHub checks both author and committer", "https://github.com/apache/superset/issues/39623 — with no identity git prints user@HOST.(none)"] }
    reasoning: "git var answers with exactly what git commit would record, so no override is missed. Upstream checks a passed-in identity; av-kit's script lets git decide, so it asks git. Never echoing stderr keeps a host or personal address out of receipts."
  - id: D-883
    stage: planning
    question: "Where does the identity check run?"
    resolution: human
    class: governance-value
    chosen: "A: inside agent-commit.ps1 in both modes, before staging and on the new commit before any push, with the git-workflow skill naming it; this session's gate also runs it once on the live repo"
    source_tag: Human-approved
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:120 — decided at plan time", "P:/agentic-framework core/tools/commit_batch.py (a73d6df) — the check runs in the commit path, not in a gate"]
    research: { engine: tavily, sources: ["https://github.com/orgs/community/discussions/172325 — pre-commit and pre-push checks for unwanted emails are the common guard"] }
    reasoning: "A commit is the only moment the address matters, and agent-commit.ps1 is the path the skill tells agents to use. A gate step lost: gates run before the commit, under a different environment. Skill text alone lost: it leaves the check manual, as today. Mat's standing ruling accepts the recommendation."
    human_message_reference: "USER_EXPLICIT 2026-11-15 \"Run HDP on any decisions that come up and and I approving acceptance of the defaults.\""
  - id: D-884
    stage: planning
    question: "Does the check accept any GitHub noreply address, or only Mat's?"
    resolution: autonomous
    class: two-way
    chosen: "Only 219344396+matbanik@users.noreply.github.com; --expected exists for tests and is never passed by the script"
    source_tag: Local Canon
    precedents: ["the user's global CLAUDE.md §Git commit identity — commits use that one address", "P:/agentic-framework core/tools/commit_batch.py:226 — upstream accepts any noreply pattern plus a config match"]
    research: { engine: none, sources: [] }
    reasoning: "Mat's rule names one address, and av-kit has one committer. The upstream pattern would pass a stranger's noreply address."
  - id: D-885
    stage: planning
    question: "What does the session gate cover?"
    resolution: autonomous
    class: two-way
    chosen: "Identity, lint, task contract, scope paths, port-check, script-check, the red-check selftest, the two new test files with no skips, the adoption tests, the full Python suite, the state render, the closeout selftest and the live identity check; types, UI, MCP, OpenAPI and build skipped"
    source_tag: Local Canon
    precedents: [".agent/docs/commands.md:190-207 — the D6 stages", "docs/execution/plans/2026-11-14-review-limits-no-token-budget/implementation-plan.md — the same shape for a tooling session"]
    research: { engine: none, sources: [] }
    reasoning: "Only Markdown, one Python tool, one script copy, one PowerShell script and two test files change."
  - id: D-886
    stage: planning
    question: "What is out of scope?"
    resolution: autonomous
    class: two-way
    chosen: "The rows of §Out of Scope"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:114-124 — Session 87's scope"]
    research: { engine: none, sources: [] }
    reasoning: "Each row is either named out by the grouping or lives outside the repository."
  - id: D-887
    stage: planning
    question: "What does this session bind to, given Sessions 84 to 86 leave uncommitted edits?"
    resolution: autonomous
    class: two-way
    chosen: "The post-Session-86 bytes, copied at row 0; scope checks by path and content, not HEAD; S2 if Session 85 changed WORKFLOW beyond the Topic too broad row"
    source_tag: Local Canon
    precedents: ["session brief — baselines path-scoped and bound to content", ".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md:91 — Session 85 edits inspiration-research.md and the git-workflow skill"]
    research: { engine: none, sources: [] }
    reasoning: "The grouping's 'shares no file with 84 to 86' (:69) is wrong for these two files. Binding to row-0 content keeps Session 85's text; the add-only check on GIT_SKILL proves none of it was lost."
```

### D-876 — Where do the provider capability snapshots live after the port?

**Recommendation:** A, keep `_inspiration/_capabilities/`. The skill is repo-local, the three tracked snapshots already live there, and `_inspiration/` is the folder `/inspiration-research` writes to.

- **Reversibility:** two-way (a path rewrite in SKILL, three templates and the stub).
- **Default if unanswered:** A.
- **Precedents:**
  - av-kit `SKILL.md` today (`_inspiration/_capabilities/`);
  - `PROJECT-PROFILE.md:103` (`_inspiration/` Keep);
  - Zorivest D-2 (`implementation-plan.md:350`, inside the skill, because it went machine-global).
- **Research:** tavily; https://www.agensi.io/learn/where-are-claude-skills-stored says project skills live in the repo with their supporting files.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|--------|--------|-----------------|-----------------|---------|
| A: keep `_inspiration/_capabilities/` (recommended) | av-kit SKILL today; `PROJECT-PROFILE.md:103` | — | — | ✅ |
| B: move into the skill's `capabilities/`, as upstream | Zorivest D-2; upstream `0a8d5bc` | Text equals upstream, so fewer adaptation rows | Moves three tracked files; separates the snapshots from the research they serve; its reason (one skill for every project) does not hold here | ⚠️ |
| C: a `capabilities_root` setting in the stub | — | Either location works | A new setting with one user; more text to keep in sync with upstream | ❌ |
| Do nothing: port the templates and script, keep the old SKILL | — | Smallest change | The old SKILL's inline templates and §5 disagree with the new files, and §6 never runs the script | ❌ |

### D-883 — Where does the identity check run?

**Recommendation:** A, inside `agent-commit.ps1`, in both modes. It runs before staging and again on the new commit before any push. The git-workflow skill names the check, and this session's gate runs it once on the live repo. This is the moment the address is written, on the path agents are told to use.

- **Reversibility:** two-way (remove four calls).
- **Default if unanswered:** A.
- **Precedents:**
  - grouping `:120` ("decided at plan time");
  - upstream `commit_batch.py`, where the check is in the commit path.
- **Research:** tavily; https://github.com/orgs/community/discussions/172325 says pre-commit and pre-push email checks are the usual guard.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|--------|--------|-----------------|-----------------|---------|
| A: `agent-commit.ps1`, both modes, plus the skill (recommended) | upstream `commit_batch.py` | — | — | ✅ |
| B: skill text only, run by hand | today's H2-5 manual check | No script change | Still advisory; a missed step writes the address | ❌ |
| C: a D6 session-gate step | `.agent/docs/commands.md:190-207` | Runs every session | Runs at the wrong time, under the gate's environment, not the commit's; does not see the exact-scope descriptor | ❌ |
| D: a git `pre-commit` hook | GitHub discussion 172325 | Catches plain `git commit` too | Hooks are local, unversioned config; installing one changes git configuration outside the repo, which Mat's rule reserves | ⚠️ |
| Do nothing: Mat's manual global rule | user CLAUDE.md | No change | The rule stays manual, which is the gap the grouping names | ❌ |

## Research References

- Upstream: `P:/agentic-framework` commits `0a8d5bc` (the skill, templates and script) and `fb00d40` (`commit_batch.py` identity refusals, read at `a73d6df`). These are primary.
- Zorivest: `P:/zorivest/docs/execution/plans/2026-10-29-deep-research-global-portal-refresh/implementation-plan.md` (D-1 `:339`, D-2 `:350`), and `P:/zorivest/.agent/context/handoffs/2026-10-29-deep-research-global-portal-refresh-implementation-critical-review.md` (R1-F1 `:20`, R1-F3 `:22`).
- https://git-scm.com/docs/git-config: identity keys and the variables that override them.
- https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables: `GIT_AUTHOR_EMAIL` and `GIT_COMMITTER_EMAIL`.
- https://github.com/apache/superset/issues/39623: git's `user@HOST.(none)` message when no identity is set.
- https://github.com/orgs/community/discussions/177282: GitHub push protection checks both author and committer.
- https://github.com/orgs/community/discussions/172325: email checks in pre-commit and pre-push hooks.
- https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address: setting `user.email` to the noreply address.
- https://www.agensi.io/learn/where-are-claude-skills-stored and https://joseparreogarcia.substack.com/p/claude-code-skills-explained: where project skills and their files live.

## Planning receipts

All of these are under `C:/Temp/av-kit/s87/`, and every probe was read-only with respect to the repository.

- **`up-skill-head.md`, `up-wf-head.md`, `up-skill-before.md`, `up-wf-before.md`, `skill-diff.txt`:** the upstream SKILL and stub before and after `0a8d5bc`, and their diff against av-kit.
- **`commit_batch.py`:** the upstream identity functions.
- **`probe/`:** a scratch repo under git 2.56.0.windows.1. It showed the following:
  - `git var` resolves both identities;
  - the variables override config;
  - `author.email` affects only the author;
  - `EMAIL` applies only when `user.email` is unset;
  - with no identity, `git var` exits 128 and names the host on stderr;
  - the live repo's identity is the expected address.
- **`precedent-sweep.txt`:** the earlier noreply mentions are the manual H2-5 author checks; no av-kit plan decided the snapshot location.
- **Line endings:** measured with Python byte counts, as in §Adaptation table and §Wiring.
- **Not run at plan time:** any test suite, any edit, `port-check.py`, `script-check.py`.

## Validation stage contract

- **Static:** `tools-lint`, `py-lint`, `task-contract`, `scope-paths`, `port-check`, `script-check`, `red-check-selftest`.
- **Targeted:** the two new test files (no skips) and the adoption tests.
- **Fresh full:** `py-tests`, `state-render`, `closeout-selftest`.
- **Runtime:** `identity-live` (AC-20), which runs the checker against the live repository and its real environment.
- **Identity:** `identity.py`, independent of the receipts. It hashes `HEAD`, plus the content of the tracked diff and the untracked files, minus this session's closeout artifacts. Other sessions' uncommitted files are therefore bound by content.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
