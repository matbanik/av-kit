---
project: "2026-11-15-triage-tool-fixes"
date: "2026-11-15"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 79; issues TOOLING-TRIAGE-CLI-CP1252 and TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS (triage D-812)"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
---

# Implementation Plan: UTF-8 output and quieter scans in the triage tool

> **Project**: `2026-11-15-triage-tool-fixes`
> **Build Plan Section(s)**: none. This is tooling debt with no MEU, as in Session 49b `2026-11-05-closeout-register-grammar` (D-280) and grouping D-815.
> **Status:** said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 2 (.agent/context/handoffs/2026-11-15-triage-tool-fixes-plan-critical-review.md).

---

## Goal

**Goal anchor:** `tools/issue_triage.py` writes UTF-8 to a redirected receipt and never crashes on a Windows console code page; `verify --deep` reports only a missing file that a path-shaped `resolution_path` names and never writes the register; and `discover` reports no candidate from a vendored or bundled tree, a binary file or its own source.

This is Session 79 of the post-rc.3 grouping (§3, "both are the triage tool this workflow runs"). Order: the encoding fix, then the scanner (grouping §3). The grouping's split flag says the session "may merge into Session 76 if Session 76's plan comes out small". **This plan is not folded into Session 76** (coordinator instruction, 2026-11-15): it keeps its own rows, its own receipts and its own review loops.

**`TOOLING-TRIAGE-CLI-CP1252`** (`known-issues.yaml:2827`). The CLI prints characters that cp1252 cannot encode: `⚠` in `_cmd_bucket` (`tools/issue_triage.py:199`) and `→` in the `render` and `migrate` help texts (`:402`, `:414`). It never reconfigures its streams. When stdout is a file or a pipe, Python uses the console code page, so the workflow's own receipt pattern crashes. Plan-time reproduction (`C:/Temp/av-kit/triage-tool-fixes/`):

- `help-noenc.txt` and `probe/help-cp1252.txt`: `--help` exits 1 on `\u2192`.
- `probe/bucket-cp1252.txt`: `bucket` on a two-issue overlap fixture exits 1 on `\u26a0`; `probe/bucket-utf8.txt`: the same run with `PYTHONIOENCODING=utf-8` exits 0 and prints `⚠ HAS RELATED OVERLAP`.

**`TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS`** (`known-issues.yaml:4040`). The 2026-11-15 triage met it again: 51 `verify --deep` findings and 14 `discover` candidates, all noise, and the register was restored to its pre-scan bytes (D-812). Plan-time reproduction on a copy of the register, with the real register's SHA-256 unchanged after every probe (`pre-hash.txt`):

| Noise class | Measured | Receipt |
|---|---|---|
| Prose in `resolution_path` read as a path | 9 `file_missing`; the census finds 48 `resolution_path` values and 0 that are a single path-shaped token | `verify-deep.txt`, `resolution-path-census.txt` |
| The blanket test-coverage check | 42 `no_test_coverage`, one per active issue except the one named in `tests/` | `verify-deep.txt` |
| `last_checked` stamped with no check | 42 issues stamped with today's date, and the copy rewritten | `ki-deep.yaml` against `ki-copy.yaml` |
| Vendored tree | 7 `.properties` and 2 `.jar` candidates under `_inspiration/external_code/shutter-encoder-master` | `discover-dry.txt` |
| Bundled tree | 3 candidates in `mcp-server/bundle/index.mjs` | `discover-dry.txt` |
| The scanner's own source | 2 candidates, `discover.py:25` and `:299` | `discover-dry.txt` |
| Generated and fetched trees, and subroots | The round-0 rules walk 110 files under 15 trees git ignores (`ui/out`, `ui/out-e2e`, `packaging/deno-win64`, `packaging/ffmpeg-win64`, `native/*/bin`, `obj` and `publish`, `test-results`, `.serena/cache`); `--root mcp-server` reports 3 `bundle/index.mjs` candidates, because the exclusion matched the path from `--root` (plan review round 1, F1) | `discover-sim2.txt`, `ignored-dirs.txt` |
| `dismissed` issues in the actionable list | `triage.py:43` archives only `resolved` | read at `triage.py:36-48` |

A simulation of this plan's discover rules over the real tree walks 829 files, none under a tree git ignores, and leaves 0 candidates; from `mcp-server`, `ui` and `packaging` it also leaves 0, and from `mcp-server/bundle` or `ui/out` it walks nothing (`discover-sim2.txt`; the round-0 `discover-sim.txt` walked 937).

**Upstream and sibling fixes** (read-only):

- **Zorivest** fixed the encoding in the same tool: `P:/zorivest/tools/issue_triage.py:402-406` reconfigures `sys.stdout` and `sys.stderr` to UTF-8 with `errors="replace"`, each inside `contextlib.suppress(AttributeError, ValueError, OSError)`. Its test runs the CLI as a subprocess under `PYTHONIOENCODING=cp1252` (`P:/zorivest/tests/unit/test_issue_triage.py:2978-2996`, `_cp1252_console_env`; commit `e2882142a`). This plan takes both shapes (D-944).
- **Zorivest** has only planned the path-shape fix: `P:/zorivest/docs/execution/plans/2026-11-05-rx6-triage-tooling-paths/implementation-plan.md` (`PATH_LIKE` at `:97`, `IGNORED_TREE_NAMES` at `:95`, the AC-3 truth table at `:119`); its issue `TRIAGE-VERIFY-PROSE-RESOLUTION-PATH` is still open (`P:/zorivest/.agent/context/known-issues.yaml:23875`). This plan adapts the truth table (D-945).
- **agentic-framework** (`a73d6df`) has no fix: `core/tools/issue_triage.py` never reconfigures its streams. `.agent/context/2026-09-18-source-project-evidence-framework-gaps.md:159` claims a fix, and `.agent/context/2026-09-19-adopter-findings-fix-proposal.md:266` records that claim as stale.
- **av-kit's own reconfigure precedents:** `tools/meu_status.py:39-47`, `tools/check_exec_review.py:34-39`, `tools/generate_third_party_licenses.py:610`.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). The change touches six named functions in four tool files and ten doc lines, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern.
  - Receipts go under `C:/Temp/av-kit/triage-tool-fixes/`, named `ttf-*`. Pytest runs with `TMP` and `TEMP` at `C:\Temp\av-kit\triage-tool-fixes\tmp`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`. The CLI tests set their own child environment, so the row's `PYTHONIOENCODING` does not mask the bug.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** not applicable; the driver OS is the target OS. The tests force cp1252 through `PYTHONIOENCODING`, so they reproduce the bug on any OS (grouping §3 "Cloud/local: either").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `ttf-plan-2026-11-15-triage-tool-fixes` and `ttf-execution-2026-11-15-triage-tool-fixes`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
- **Queue:** Session 87 runs and is committed first. Sessions 75 to 78 run before this one, and Mat has not said whether each is committed after it closes, so their changes may be uncommitted when this session starts. Baselines and scope checks are path-scoped and bound to content (§Verification Plan 1). Execution waits for Mat's message (`plan_to_exec_gate: human`).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| Both issues (no MEU) | `.agent/context/handoffs/2026-11-15-triage-tool-fixes-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-triage-tool-fixes-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-triage-tool-fixes-implementation-critical-review.md`

One handoff for the session follows the no-MEU precedent `2026-11-05-closeout-register-grammar-handoff.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, BASE copies, `ttf-base-py.txt`, `ttf-ruff-base.txt` |
| WP-2 | Encoding: Red, then Green (rows 1 and 2) | WP-1 | shared | `tests/unit/test_issue_triage.py`, `tools/issue_triage.py` |
| WP-3 | `verify --deep`: Red, then Green (rows 3 and 4) | WP-2 | shared | `tools/issue_triage/verify.py`, `tools/issue_triage.py` |
| WP-4 | `discover`: Red, then Green (rows 5 and 6) | WP-3 | shared | `tools/issue_triage/discover.py` |
| WP-5 | `triage` archive: Red, then Green (rows 7 and 8) | WP-4 | shared | `tools/issue_triage/triage.py` |
| WP-6 | Docs, live smoke, register (rows 9 to 11) | WP-5 | shared | The five docs, `ttf-live-smoke.txt`, `known-issues.yaml` and `.md`, grouping §6 row 79 |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling.** Two choices had no settled answer in the files (D-946 and D-947, the briefs at the end of §Decision Log). Each has only an M-6 hit, so your 2026-11-15 hand-over for this grouping covers it, and each is recorded as the agent's choice. One line from you overturns either.
>
> **What changes for you:**
>
> - `issue_triage.py` output can be redirected to a receipt on Windows without a crash, with no `PYTHONIOENCODING` workaround.
> - `verify --deep` reports a missing file only when `resolution_path` is a path, not a sentence; a trailing line number such as `:199` is ignored when it looks the file up. It no longer reports "no test references the issue ID" for 42 of the 43 active issues (D-946).
> - `verify --deep` no longer writes `verification.last_checked`. A triage that really re-checks an issue sets the date, method, result and evidence file itself, by hand in the YAML (D-947). From 2026-12-05, plain `verify` flags as stale the 30 issues whose date the 2026-11-04 deep run stamped; nobody checked them that day, so the flag is accurate.
> - `discover` no longer reports markers from the trees `.gitignore` marks as generated, fetched or vendored (`ui/out`, `mcp-server/bundle`, `packaging/deno-win64`, `_inspiration/external_code` and the rest), from binary files or from its own source, whichever `--root` it is given (D-948, D-953).
> - `triage --output` puts dismissed issues in `archived`, beside resolved ones.
>
> **What this plan leaves out:** reformatting the four tool files (they have three ruff findings and would be reformatted today), regenerating `triage-output.yaml`, and moving TECH-DEBT, MONITORING and BLOCKED issues out of `actionable` (§Out of Scope).

## Proposed Changes

### Single-statement contracts

- **`UTF8_STREAMS` (D-944):** `main(argv)` in `tools/issue_triage.py` begins, before it builds the parser, with `for stream in (sys.stdout, sys.stderr):` and `stream.reconfigure(encoding="utf-8", errors="replace")` inside `contextlib.suppress(AttributeError, ValueError, OSError)`, the Zorivest shape. `_cmd_discover`'s `_safe_print` stays.
- **`PATH_LIKE` (D-945):** `tools/issue_triage/verify.py` gains `_is_path_like(value: object) -> bool`. A non-`str` gives `False`. Otherwise `s = value.strip()` is path-like when `s` is non-empty, holds no whitespace, does not hold `://`, and either holds `/` or `\` or has a non-empty `PurePosixPath(s).suffix`.
- **`PATH_LOCATION` (D-945):** `verify.py` gains `_strip_location(s: str) -> str`. It returns `re.sub(r"(?::\d+){1,2}$", "", s)` when that is non-empty, and `s` otherwise: a trailing colon and digits, once or twice (a line, or a line and a column), go. A drive colon (`C:\`, `C:/`) is never followed by digits up to the end, so it stays.
- **`PATH_CHECK` (D-945):** `verify_deep` checks `resolution_path` only when `_is_path_like` holds, against `root / p` with `p = _strip_location(value.strip())`, with the existing `(OSError, ValueError)` guard. A missing path gives one `file_missing` finding with `evidence_path` `str(root / p)`, the path without its line and column. A value that is not path-like gives no finding.
- **`NO_COVERAGE_CHECK` (D-946):** `verify_deep` no longer reads `tests/` and never emits `no_test_coverage`. `file_missing` is its only finding type.
- **`DEEP_READ_ONLY` (D-947):** `verify_deep(data, *, project_root=None)` has no `update_last_checked` parameter and never changes `data`. `_cmd_verify`'s `--deep` branch never calls `save`. It still exits 1 when there are findings and 0 when there are none. The docstring lists only what it checks; the never-emitted `fix_indicator_found` goes.
- **`DISCOVER_ROOTS` (D-948):** the exclusions mirror every directory pattern of `.gitignore`. `EXCLUDED_DIRS` gains the slash-free ones it lacks: `bin`, `Bin`, `obj`, `Obj`, `test-results`, `playwright-report`, `blob-report`, `.playwright` and `htmlcov`. `EXCLUDED_PATHS` becomes `{"docs/execution", "_inspiration/external_code", "mcp-server/bundle", "mcp-server/dist", "ui/out", "ui/out-e2e", "ui/dist", "packaging/build", "packaging/dist", "packaging/ffmpeg-win64", "packaging/deno-win64", "native/*/publish", ".serena/cache"}`. A directory is skipped when its name is in `EXCLUDED_DIRS` or when `fnmatch.fnmatchcase(rel, pattern)` holds for one `EXCLUDED_PATHS` pattern, `rel` being its repository path (`DISCOVER_ANCHOR`); `*` matches across `/`, as `**` does in `.gitignore:30`. No tracked file lies under an added entry, and `ui/src`, `mcp-server/src`, `packaging/*.spec`, `packaging/licence-overrides`, `native/*/` sources and `_inspiration`'s notes stay in scope (`discover-sim2.txt`).
- **`DISCOVER_ANCHOR` (D-953):** `discover._repo_root(root: Path) -> Path` returns the first of `root.resolve()` and its parents that holds a `.git` entry (a directory or a file), or `root.resolve()` when none does. `scan_todos` passes it to `_walk_source_files(directory, anchor)`, which matches each directory's `item.resolve().relative_to(anchor).as_posix()` and falls back to `item.name` on `ValueError`, as today. Before it walks, `scan_todos` returns `[]` when the scan root lies in an excluded tree: one part of `root.resolve().relative_to(anchor).parts` is in `EXCLUDED_DIRS`, or a leading run of those parts, joined with `/`, matches an `EXCLUDED_PATHS` pattern. A finding's `file_path` stays relative to the scan root.
- **`DISCOVER_BINARY` (D-948):** `scan_todos` reads each file once with `read_bytes()`, skips it when its first 8,000 bytes hold `b"\x00"`, and decodes the rest with `decode("utf-8", errors="ignore")`.
- **`DISCOVER_SELF` (D-948):** `discover._SELF = Path(__file__).resolve()`, and `scan_todos` skips a file whose `resolve()` equals it. A different file named `discover.py` is scanned.
- **`ARCHIVE_DISMISSED` (D-949):** `generate_triage_output` puts an issue whose `status` is `resolved` or `dismissed` in `archived`. The other two sections keep their rules. The docstring says "archived: resolved and dismissed issues".
- **`DEEP_HELP` (D-950):** the `--deep` help text becomes `Check that path-shaped resolution_path values exist (read-only)`.
- **`DOC_LINES` (D-950):** the ten line edits of `doc-check.py`'s `TABLE` (§The docs), and no other doc change.

### The docs

`doc-check.py` holds the edits as a table of old and new lines. Each edit keeps its file's line endings.

| File | Line endings | Edit |
|---|---|---|
| `.agent/workflows/issue-triage.md` | CRLF, kept | `:93`, the note under "Use `issue_triage.py verify --deep`", says it checks path-shaped `resolution_path` values and only reads the register. `:103` and `:104`, the `no_test_coverage` and `fix_indicator_found` bullets, are removed. `:271` says "resolved and dismissed issues" |
| `.agent/skills/issue-triage/SKILL.md` | LF, kept | `:41`, the comment becomes `# Deep verify: path-shaped file checks; read-only` |
| `.agent/docs/issue-lifecycle-guide.md` | CRLF, kept | `:118-122`, five bullets, become two (the path check; read-only). `:397`, the comment. `:461`, the box line, at the same width. `:549`, "Check if issues are stale" runs `verify`, not `verify --deep` |
| `.agent/docs/commands.md` | CRLF, kept | `:46`, the comment becomes `# Deep verify: path-shaped file checks; read-only` |
| `.agent/docs/cloud-local-collaboration.md` | CRLF, kept | `:291`, "(file existence, test references)" becomes "(path-shaped file checks)" |

A plan-time probe applied the table to the live files: each anchor is found once, each file keeps its line endings, and no removed claim remains (`doc-check-anchor-probe.txt`). `doc-check.py --selftest` passes 9 of 9 (`doc-check-selftest.txt`).

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `issue_triage.py` stdout and stderr | `tools/issue_triage.py` `main` | UTF-8 with `errors="replace"`; text otherwise unchanged | Unchanged |
| `verify --deep` findings | `tools/issue_triage/verify.py` | `type` is only `file_missing`; the dict keys `issue_id`, `type`, `message`, `evidence_path` are unchanged | Unchanged |
| `known-issues.yaml` under `verify --deep` | `tools/issue_triage/model.py` | Not written | — |
| `discover` candidates | `tools/issue_triage/discover.py` | Dict keys unchanged | Unchanged |
| `triage-output.yaml` sections | `tools/issue_triage/triage.py` | `archived` gains dismissed issues | Unchanged |

No API route, OpenAPI document, MCP tool shape, database schema or product package changes. No caller of `verify_deep`, `update_last_checked`, `generate_triage_output` or `scan_todos` exists outside `tools/issue_triage*` (plan-time `rg`).

### Acceptance Criteria

Every test is in `tests/unit/test_issue_triage.py` (new, LF) and is named `test_ac_<n>_…`, so `red-check.py --require test_ac_<n>` matches each exactly.

- **Imports.** The package imports as `from tools.issue_triage import discover, model, triage, verify` (pytest `pythonpath` holds `.`; precedent `tests/unit/test_deps_report.py`).
- **CLI tests run as a subprocess:** `[sys.executable, str(ROOT / "tools/issue_triage.py"), "--yaml", str(f), …]` with `cwd` at a temporary folder and an explicit child environment. That keeps pytest's own streams out of the test. Zorivest's `_cp1252_console_env` is the shape.
- **Markers.** Every marker string in the test file is built by concatenation (`"TO" + "DO"`), so the test file never becomes a `discover` candidate itself.
- **New names fail by assertion.** Each test asserts a new name exists (`hasattr(verify, "_is_path_like")`, `hasattr(discover, "_SELF")`) before it uses it, so Red fails by assertion, never by `AttributeError` in setup (Session 52 RULE-4).

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-1 | unit (subprocess) | `--help` with `PYTHONIOENCODING=cp1252` and `PYTHONUTF8=0` exits 0, and its stdout bytes hold `b"\xe2\x86\x92"` (`→` in UTF-8). | Local Canon (`TOOLING-TRIAGE-CLI-CP1252` blast_radius; `tools/meu_status.py:39-47`; Zorivest `test_issue_triage.py:2978-2996`; D-944) | Control: the same environment makes `python -c "import sys; print(sys.stdout.encoding)"` print `cp1252`, so the test reproduces the bug |
| AC-2 | unit (subprocess) | `bucket` on a two-issue overlap fixture (two open `MEU-NEW` infrastructure issues sharing a `related` tag, with `root_cause` and `blast_radius`) under the same cp1252 environment exits 0, and stdout decoded as UTF-8 holds `⚠ HAS RELATED OVERLAP`. | Local Canon (the issue's root_cause; D-944) | Today it exits 1 with `UnicodeEncodeError` (`probe/bucket-cp1252.txt`) |
| AC-3 | unit | `_is_path_like` truth table. True: `packages/core/nonexistent.py`, `tools\x.py`, `README.md`, `"  ui/a.tsx  "`. False: `""`, `"   "`, a sentence with a path inside it, `https://example.com/a.py`, `MEU-123`, `deferred`, `None`, `42`. Also True: `tools/issue_triage.py:199`, `C:\x\a.py:12:3`. `_strip_location` gives `tools/issue_triage.py` for `tools/issue_triage.py:199`, `a.py` for `a.py:12:3`, `C:\x\a.py` for `C:\x\a.py:7` and `C:/x/a.py` for `C:/x/a.py:7:1`, and leaves `C:\x\a.py`, `a.py:x` and `:12` unchanged. | Local Canon (the issue's resolution_path "accept only path-shaped tokens"; Zorivest RX6 AC-3; D-945; plan review round 1, F2) | The False rows and the unchanged `_strip_location` rows |
| AC-4 | unit | `verify_deep(data, project_root=tmp)` on five open issues: a prose `resolution_path` gives no finding; `missing/file.py` gives exactly one `file_missing` with `evidence_path == str(tmp / "missing/file.py")`; `gone/other.py:9:2` gives exactly one with `evidence_path == str(tmp / "gone/other.py")`; an existing `present.py` and `present.py:3` give none. There are two findings in all. | Local Canon (D-945; plan review round 1, F2) | The prose and existing cases; `present.py:3` is a false `file_missing` today |
| AC-5 | unit | With a `tests/` folder in `tmp` whose files never name the issue ids, `verify_deep` emits no `no_test_coverage`, and the set of finding types is a subset of `{"file_missing"}`. | Local Canon (D-946, handed to the agent) | Today 42 of the 43 active issues get one (`verify-deep.txt`) |
| AC-6 | unit + subprocess | `inspect.signature(verify_deep)` has no `update_last_checked`; a `copy.deepcopy` of the data equals the data after the call. The CLI `--yaml f verify --deep` with `cwd=tmp` leaves `f`'s bytes unchanged, exits 1 when a path-like reference is missing, and exits 0 when the only `resolution_path` is prose. | Local Canon (D-947, handed to the agent) | The exit-0 case; today the copy is rewritten (`ki-deep.yaml`) |
| AC-7 | unit | With `tmp/.git` created (an empty folder), `scan_todos(tmp)` reports no candidate from the noise files `_inspiration/external_code/x/a.properties`, `mcp-server/bundle/index.mjs`, `ui/out/main/index.js`, `ui/out-e2e/main/index.js`, `packaging/deno-win64/LICENSE.md`, `packaging/ffmpeg-win64/README.txt`, `native/region-picker/publish/a.xml`, `native/region-picker/obj/a.cs`, `ui/test-results/a.md` and `.serena/cache/a.txt`, and reports exactly the five controls `_inspiration/design.md` (`<!-- TODO -->`), `mcp-server/src/a.ts` and `ui/src/a.ts` (`// TODO`), `packaging/avkit-backend.spec` and `native/region-picker/a.cs`. `discover._repo_root(tmp / "mcp-server")` is `tmp.resolve()`; `scan_todos(tmp / "mcp-server")` reports only `src/a.ts`; `scan_todos(tmp / "mcp-server/bundle")` and `scan_todos(tmp / "ui/out")` return `[]`. | Local Canon (the issue's root_cause; `.gitignore`; D-948; D-953; plan review round 1, F1) | The five controls and the subroot's `src/a.ts` |
| AC-8 | unit | A `lib/x.jar` whose first bytes hold a NUL byte and whose text holds a marker is skipped; a `notes.txt` control with a marker is reported. | Local Canon (D-948) | The `notes.txt` control |
| AC-9 | unit | `scan_todos(ROOT / "tools/issue_triage")` reports nothing from `discover.py`; a file named `discover.py` in `tmp` with a marker comment is reported. | Local Canon (the issue's root_cause, `discover.py:25,299`; D-948) | The `tmp` copy named `discover.py` |
| AC-10 | subprocess | The CLI `--yaml f discover --root <tmp> --dry-run`, on a tree holding `.git`, the AC-7 and AC-8 noise files and the five AC-7 controls, prints `New candidates: 5` and only the five controls (paths compared with `/`). With `--root <tmp>/mcp-server` it prints `New candidates: 1`, and with `--root <tmp>/mcp-server/bundle` `New candidates: 0`. `f`'s bytes are unchanged. | Local Canon (D-948; D-953) | Today the noise files are listed, and the subroot reports `bundle/index.mjs` |
| AC-11 | unit | `generate_triage_output` on a resolved, a dismissed, an open TECH-DEBT and an open `DEFER` issue puts the first two in `archived`, the TECH-DEBT issue in `actionable` and the `DEFER` issue in `deferred`. | Local Canon (the issue's root_cause, `triage.py:43-48`; D-949) | The `actionable` and `deferred` placements |
| AC-12 | doc check | `doc-check.py --check` exits 0: each of the five docs equals its row-0 copy with `TABLE` applied, byte for byte, with its line endings kept, and no removed claim remains. The new `issue-triage.md` note names `verification.last_checked`, `method`, `result` and `evidence_file` together and says the triaging agent sets them by hand (`cloud-local-collaboration.md:316`). `doc-check.py --selftest` exits 0, including its check of that note. | Local Canon (D-950; D-947) | The selftest's six failing cases |
| AC-13 | live smoke | `live-smoke.py` exits 0: on a copy of the real register, `verify --deep` (in process and through the CLI) gives no `no_test_coverage`, and each `file_missing` names a path-like value (printed `real:`); the copy is unchanged. `discover --dry-run` from `.` and from the subroots `mcp-server`, `ui` and `packaging` gives no noise-class candidate (noise: a tree that `git ls-files --others --ignored --exclude-standard --directory` lists, one of `DISCOVER_ROOTS`'s trees, the scanner's own module, a `.jar`, a file with a NUL byte), any other candidate is printed `real:`, each CLI count equals the in-process count, `_repo_root` of each subroot is the repository, and no walk lists a file under a noise tree; the walk from `.` lists `tools/issue_triage.py` and more than 500 files. A root inside `mcp-server/bundle` or `ui/out` (when present) gives 0 in process and through the CLI. Every inventoried tree on disk classifies as noise, so an omitted tree fails the smoke instead of printing `real:`. `--help` under cp1252 exits 0. The real register's SHA-256 is unchanged. | Local Canon (D-812; D-944 to D-948; D-953) | Each `PROBLEM:` line; expected `verify_deep findings 0` and `scan_todos new candidates 0` from the plan-time census and simulation |
| AC-14 | register | Both issues are `resolved` through `issue-resolve.py` bound to row 0's register hash; `issue_triage.py render` and `render --check` exit 0; the register stays LF; grouping §6 row 79 says `executed (Session 79)` with this plan folder. | Local Canon (`issue-triage.md` §Closing; Session 84's row 7) | `issue-resolve.py` refuses a register whose hash moved (S4) |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| How the streams become UTF-8 | Local Canon | Reconfigure at `main`, the Zorivest and `meu_status.py` shape (D-944) |
| Which `resolution_path` values are paths | Local Canon | The whole value, path-shaped; a trailing line and column are dropped before the lookup (D-945) |
| What happens to the test-coverage finding | Local Canon (handed to the agent) | Removed (D-946) |
| Whether `verify --deep` writes the register | Local Canon (handed to the agent) | Never (D-947) |
| Which trees and files `discover` skips | Local Canon | `.gitignore`'s directory trees, NUL-byte files, its own module (D-948) |
| Which path the exclusions match | Local Canon | The repository path; a root inside an excluded tree gives nothing (D-953) |
| Where dismissed issues go | Local Canon | `archived` (D-949) |
| Which docs change | Local Canon | The ten lines of `doc-check.py` (D-950) |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `tools/issue_triage.py` | modify | LF, kept | `UTF8_STREAMS` (`import contextlib`), `DEEP_READ_ONLY` in `_cmd_verify`, `DEEP_HELP` |
| `tools/issue_triage/verify.py` | modify | CRLF, kept | `_is_path_like`, `PATH_CHECK`, `NO_COVERAGE_CHECK`, `DEEP_READ_ONLY`, the docstring |
| `tools/issue_triage/discover.py` | modify | LF, kept | `DISCOVER_ROOTS`, `DISCOVER_BINARY`, `DISCOVER_SELF` |
| `tools/issue_triage/triage.py` | modify | LF, kept | `ARCHIVE_DISMISSED`, the docstring |
| `tests/unit/test_issue_triage.py` | new | LF | AC-1 to AC-11 |
| `.agent/workflows/issue-triage.md` | modify | CRLF, kept | §The docs |
| `.agent/skills/issue-triage/SKILL.md` | modify | LF, kept | §The docs |
| `.agent/docs/issue-lifecycle-guide.md` | modify | CRLF, kept | §The docs |
| `.agent/docs/commands.md` | modify | CRLF, kept | §The docs |
| `.agent/docs/cloud-local-collaboration.md` | modify | CRLF, kept | §The docs |
| `.agent/context/known-issues.yaml` | modify (tool) | LF, kept | The two issues resolved through `issue-resolve.py` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modify | LF, kept | §6 row 79 only: `executed (Session 79)` and this plan folder |

Line endings and sizes were measured with Python bytes at `HEAD` `6aaf9b0`: `issue_triage.py` 15,643 bytes, `verify.py` 8,784, `discover.py` 9,427, `triage.py` 2,529, `issue-triage.md` 15,004, `SKILL.md` 4,823, `issue-lifecycle-guide.md` 25,427, `commands.md` 18,357, `cloud-local-collaboration.md` 26,327, `known-issues.yaml` 455,210, `known-issues.md` 7,182, the grouping 31,451. A CRLF file is read and written with `newline=""` from CRLF text, and the session gate checks every file in this table again.

### Project files

- **Plan-local scripts**, all in this plan folder (LF): `baseline.ps1`; `red-check.py` (copied from `2026-11-15-framework-small-syncs`, unchanged); `identity.py` (the same copy with this plan's `PLAN`); `issue-resolve.py` (copied from `2026-11-15-closeout-record-once` with `SCRATCH` at `C:/Temp/av-kit/triage-tool-fixes/issue-resolve`); `doc-check.py`; `live-smoke.py`; `session-gate.ps1` (written at H1-2).
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json` and the BASE copies), not to `HEAD`, and changes only its own entries or lines in it.

| File | Siblings | Rule |
|---|---|---|
| `tools/issue_triage*` | None: Session 79 only (grouping §2 soft order) | Row 0 stops on S2 if a code file differs from `HEAD` |
| `.agent/context/known-issues.yaml`, `known-issues.md` | Sessions 75 to 78 and 80 to 82 close their own issues; Session 83 edits the lines that name the home folder (grouping §2 soft order) | Session 83 runs after this one. Row 11 changes only the two issues' `status`, `verification` and `resolution_path`, names no home path, and binds to the row-0 hash (S4) |
| `.agent/docs/commands.md`, `.agent/docs/cloud-local-collaboration.md`, `.agent/workflows/issue-triage.md`, `.agent/docs/issue-lifecycle-guide.md` | Sessions 85 and 86 (HDP v2) edited these files and are committed (`6aaf9b0`); no Session 75 to 83 plan names them | Row 9 edits through the row-0 copies; each anchor must still be found once (S2) |
| Grouping §6 table | Every session of the grouping | Only row 79 changes |
| `tests/unit/` | None. Session 76 (`tooling-test-hermeticity`) edits `tests/tooling/` only | The new file is `tests/unit/test_issue_triage.py`, never `tests/tooling/` |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

**The adoption fixture does not pin these files.** `tests/tooling/test_framework_adoption.py`'s `migrated_tree` fixture (`:369-392`) copies the live bytes, and the tests that use it run only `verify(root, "static")` (`:412`, `:438`); the hash comparisons of `file_state` in `docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py` (`:97`) run only in the baseline, final and closeout modes, which the tests drive with synthetic fixtures. The live `verify.py` (`6597ca77…`) and `model.py` (`5b738425…`) already differ from their manifest preimages while those tests pass. So this plan needs nothing from Session 76; the gate still runs the adoption tests as a targeted step.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Reformatting the four tool files and fixing their three existing ruff findings (`I001` at `issue_triage.py:222` and `verify.py:146`, `E501` at `verify.py:52`) | out-of-scope | — | Neither issue names them; a reformat would bury the fix in the diff. The gate allows no new finding (§Session gate) |
| Regenerating `.agent/context/triage-output.yaml` | out-of-scope | — | It is regenerated by the next `/issue-triage` run (D-949) |
| Moving TECH-DEBT, MONITORING and BLOCKED issues out of `actionable` | out-of-scope | — | The issue names it beside the dismissed case, but which categories are actionable is a triage rule, not a tool fault (D-949) |
| Extracting path tokens from prose in `resolution_path` | out-of-scope | — | D-945 |
| A narrower test-coverage check (mitigated issues only, or a new field) | out-of-scope | — | D-946 |
| Reading `.gitignore` at run time, or file-level ignores (`.coverage`, `*.tsbuildinfo`, `undefined`) | out-of-scope | — | D-948 mirrors the directory patterns; a single file is read like any other file, under the NUL test and the comment rules |
| `ui/build/`, which is tracked (icons and `installer.nsh`) and already skipped by the existing `build` name | out-of-scope | — | An existing exclusion this plan does not change; `installer.nsh` holds no marker |
| A port to agentic-framework or Zorivest | out-of-scope | — | Read-only references (session brief) |
| The renderer, the API, MCP, E2E, MEU-144 and the TTS model assets | out-of-scope | — | No product file changes; Session 74 is outside this run |

## BUILD_PLAN.md Audit

This session has no MEU, so `meu-status.yaml`, `meu-registry.md` and `docs/BUILD_PLAN.md` don't change. H1-3 confirms the render:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/triage-tool-fixes/ttf-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/triage-tool-fixes/ttf-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. **Tree state.** It records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`. Sessions 75 to 78 may be listed there.
2. **Path-scoped baseline.**
   - It writes `baseline-scope.json`: for each path in §Files Modified, its SHA-256, or `absent`. The new test file must be `absent`.
   - It writes `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`. S4 and the gate's `scope-paths` compare against it.
   - It copies every existing §Files Modified file to `C:/Temp/av-kit/triage-tool-fixes/base/`.
3. **Bindings (S2).** Each of the four code files must equal its `HEAD` blob (`git cat-file --filters`): a code file that differs is S2, because another session changed code this plan edits. Each `doc-check.py` anchor must be found exactly once in its BASE copy: a doc that an earlier session changed elsewhere is fine.
4. **Base receipts.** It runs `uv sync --frozen --all-packages` and the base Python suite (`ttf-base-py.txt`), with `TMP` and `TEMP` at `C:\Temp\av-kit\triage-tool-fixes\tmp`, and records the four tool files' ruff findings (`ttf-ruff-base.txt`; three at plan time).
5. **Selftests.** `red-check.py`, `identity.py` and `doc-check.py`.

If any fail-fast step fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require test_ac_<n>` checks every AC test of the row.
- **New names fail by assertion.** Each test asserts the new name exists before it uses it.
- **One test file, four Red rows.** Row 1 writes the whole file, AC-1 to AC-11, and runs only AC-1 and AC-2; rows 3, 5 and 7 run their own ACs with `-k`. The file is never edited after row 1 except to fix setup (S3).
- **Assertion messages are one line.** A CLI test's message is a `repr` of the exit code and a stderr tail, never the raw multi-line stderr: `red-check.py` reads each pytest `E` line that names an `…Error`, and a raw `UnicodeEncodeError` line would be refused as a non-assertion diagnostic.
- **Expectations stay immutable in Green.** A Green row that needs a changed expectation stops on S3.
- **Line endings.** `verify.py` is CRLF; it is measured with Python bytes and written with `newline=""`.

### Session gate (H1-2)

`session-gate.ps1` follows the peer's shape (`2026-11-15-closeout-record-once/session-gate.ps1`):

- one receipt per step in `C:/Temp/av-kit/triage-tool-fixes/`, named `ttf-D6-<step>`;
- fail-fast, with later steps printed as `not_run`;
- the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-lint` (`ruff check packages/ tests/`); `tools-lint` (`ruff check --output-format concise` on the four tool files: every `(path, code)` pair must be in `ttf-ruff-base.txt`); `py-format` (`ruff format --check tests/unit/test_issue_triage.py`); `task-contract`; `scope-paths` (every changed path is in §Files Modified, in this plan folder, in the closeout artifacts or in `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps its row-0 content state); `line-endings` (each §Files Modified file keeps its row-0 kind); `doc-check` (`doc-check.py --check`); `red-check-selftest` |
| Targeted | `triage-tests` (`tests/unit/test_issue_triage.py`); `register-callers` (`tests/tooling/test_closeout_record_once.py` and `test_closeout_register_grammar.py`, which import `issue_triage.model`); `adoption` (`tests/tooling/test_framework_adoption.py`); `live-smoke` (`live-smoke.py`) |
| Fresh full | `py-tests` (`pytest tests/ --tb=short -q -rfE`); `state-render` (`meu_status.py render --check`); `issues-render-check` (`issue_triage.py render --check`) |
| Skipped, with reason | `py-types`: `pyright` covers `packages/` only (`pyproject.toml` `[tool.pyright] include`), and nothing there changes. `ui-*`: nothing under `ui/` changes. `mcp-*`: no MCP change; the MCP Python tests run inside `py-tests`. `e2e`: no renderer or launch change. `openapi`: no `packages/api` change (H1-4). `build-record`: no build |

`py-tests` excuses only ids that row 0's receipt shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a code file of §Files Modified changed since `HEAD`, or a `doc-check.py` anchor missing or repeated in its BASE copy | Stop. An earlier session changed a file this plan edits; bring the diff to Mat |
| S3 | A Red receipt fails `red-check.py`, or a Green row needs a changed expectation | Fix the test setup; do not move to Green, and never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path changes content, or `known-issues.yaml` no longer has its row-0 hash at row 11 | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test fails after Green, or `live-smoke.py` prints a `PROBLEM:` line that the plan's contracts do not explain | Stop: an existing test is an M-7 question (§4a), not a fix; a smoke problem goes to Mat with the receipt |
| S6 | Codex is unavailable or the ledger refuses | Mat |

## Decision Log

> [!NOTE]
> D-944, D-945 and D-948 to D-953 are autonomous with `mandatory: none`: each passed the §4a list and the §4 test. D-946 and D-947 failed the convergence test (the issue proposes two options for each, and the files do not settle them), so each has a brief below; each has only an M-6 hit, so Mat's hand-over for this grouping applies and each is recorded as `autonomous`. D-812 (triage) is applied, not re-recorded. The grouping rows D-813, D-815 and D-816 stay in the grouping file's §8 and are not copied here; H2-2 reads them through `--decision-source` on the grouping file (this plan's `grouping_source`), and the two issues' logs through `--decision-issue`. The grouping's old "Carry-forward" wording (§9, "each row appears in its consuming session's reflection") is ignored under the new HDP §6: the reflection's `### Decisions Log` lists only this session's reversible autonomous choices. This session is not folded into Session 76 (D-952). D-953 was added for plan review round 1 (F1), and D-945 and D-948 were widened there (F2, F1); D-954 is left free for execution.

```yaml
decision_log:
  - id: D-944
    stage: planning
    question: "How does issue_triage.py stop crashing when its output goes to a file on Windows?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Reconfigure sys.stdout and sys.stderr to UTF-8 with errors=replace at the start of main(), each inside contextlib.suppress(AttributeError, ValueError, OSError), before the parser is built. Keep _safe_print."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:2827 — TOOLING-TRIAGE-CLI-CP1252 proposes sys.stdout.reconfigure(encoding='utf-8') at CLI entry plus a redirected-output test"
      - "P:/zorivest/tools/issue_triage.py:402-406 — the sibling fix of the same tool, the same shape"
      - "tools/meu_status.py:39-47 — av-kit's own CLI reconfigures its streams the same way"
    research: { engine: none, sources: [] }
    reasoning: "The issue, the sibling fix and av-kit's own CLIs agree. Reconfiguring at main covers every subcommand, the argparse help included, which a per-print fallback like _safe_print cannot. Replacing the arrows and the warning sign with ASCII lost because the next non-ASCII title in the register would crash again. Setting PYTHONIOENCODING in each workflow lost because every caller has to remember it. errors=replace keeps a lone surrogate from crashing a print. Two-way: four lines."
  - id: D-945
    stage: planning
    question: "Which resolution_path values does verify --deep treat as a file to check?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Only a whole value that is path-shaped once trimmed: not empty, no whitespace, no ://, and either a slash or backslash or a file suffix. A trailing colon and digits, once or twice (a line, or a line and a column), are dropped before the lookup and in the evidence path; a drive colon stays. Any other value gives no finding."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:4040 — the issue proposes accepting only path-shaped tokens"
      - "P:/zorivest/docs/execution/plans/2026-11-05-rx6-triage-tooling-paths/implementation-plan.md:97 — the sibling's planned PATH_LIKE rule and its truth table at :119"
      - "C:/Temp/av-kit/triage-tool-fixes/resolution-path-census.txt — 48 values, 0 of them a single path-shaped token; the 9 file_missing findings are all prose"
      - "C:/Temp/av-kit/ttf-plan-review-round-1.md — F2: tools/issue_triage.py:199 passes the shape test and the literal lookup reports the existing file missing"
    research: { engine: none, sources: [] }
    reasoning: "The register writes resolution_path as prose about the fix, and the census finds no value that is only a path, so every finding today is noise. A whole-value rule removes that noise and still catches a value that is a path. Pulling path-like tokens out of the prose lost: a sentence that mentions a file is not a claim that the file must exist, and a file named in a plan for future work would be reported as missing. Dropping the check entirely lost because a real path value would then go unchecked. A value with a line annotation names a file, so its file is checked: reading it literally lost because an existing file would be reported missing, and treating it as not a path lost because a moved file would then go unreported. The rule takes only digits after the last one or two colons, so a drive colon is never touched. Two-way: two helpers."
  - id: D-946
    stage: planning
    question: "What happens to the test-coverage finding that verify --deep reports for nearly every active issue?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "Remove the check: verify --deep stops reading tests/ and never emits no_test_coverage."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:4040 — the issue proposes to drop or narrow no_test_coverage, without choosing"
      - "C:/Temp/av-kit/triage-tool-fixes/verify-deep.txt — 42 of the 43 active issues get the finding"
      - "C:/Temp/av-kit/ttf-expert-st.txt — census: 1 of 43 active and 0 of 90 resolved issues are named in tests/"
      - ".agent/context/known-issues.yaml — enrichment.decision_log D-812: the second triage in a row where the scans add no signal"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling of the same day ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set, and this item has only an M-6 hit. The check runs on every active issue (verify.py:187 skips resolved, candidate and dismissed ones) and flags 42 of 43; the one it skips is the only active issue named in tests/, and none of the 90 resolved issues is named there, so a missing test name is no signal. What removal loses is the note that an active or mitigated issue has no test naming it; a triage can search tests/ itself. Narrowing it to status mitigated lost although it is one condition and gives 1 finding today: with 0 of 90 resolved issues named in a test, that finding is the normal case, not a warning. Narrowing it to issues that claim a test lost because no record field holds that claim. Keeping it as information only lost because 42 lines of information still bury the real findings. Not an M-11 hit: verify --deep is advisory and gates nothing. Two-way: the check can come back as its own subcommand."
  - id: D-947
    stage: planning
    question: "Does verify --deep still write verification.last_checked into the register?"
    resolution: autonomous
    class: source-conflict
    mandatory: [M-6]
    chosen: "No. verify --deep only reads the register: verify_deep loses its update_last_checked parameter and never changes the data, and the CLI never saves."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:4040 — the issue proposes stamping last_checked only when a check ran"
      - ".agent/context/known-issues.yaml — enrichment.decision_log D-812: the triage reverted the stamps byte for byte, because nothing was checked"
      - ".agent/docs/cloud-local-collaboration.md:316 — a verification sets last_checked, method, result and evidence_file together"
      - "C:/Temp/av-kit/ttf-expert-lc.txt — 29 of 43 active issues have a last_checked date and no method or result"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The quote applies Mat's default-acceptance ruling of the same day ('Run HDP on any decisions that come up and and I approving acceptance of the defaults.') to this brief set, and this item has only an M-6 hit. A date in last_checked is read as evidence that someone checked the issue, and cloud-local-collaboration.md:316 sets it together with method, result and evidence_file. The tool's only check is whether a path exists, which is not a check of the issue, and for most issues it checks nothing at all. Stamping only when a path check ran lost for that reason; 29 of the 43 active issues already carry a date with no method or result. An opt-in --stamp flag lost for the same reason. After the change the triaging agent sets the four fields together by hand in the YAML when it really re-checks an issue; issue-triage.md says so, and doc-check.py pins that text. The cost is that plain verify flags as stale the 30 active issues stamped by the 2026-11-04 deep run, from 2026-12-05 (verify.py:60 compares with a strict less-than); the flag is accurate, and no workflow step or gate runs plain verify. Two-way: a parameter can return."
  - id: D-948
    stage: planning
    question: "Which files does discover skip so that it reports no vendored, bundled, binary or self-made candidates?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Mirror every directory pattern of .gitignore: add bin, Bin, obj, Obj, test-results, playwright-report, blob-report, .playwright and htmlcov to EXCLUDED_DIRS, and make EXCLUDED_PATHS docs/execution, _inspiration/external_code, mcp-server/bundle, mcp-server/dist, ui/out, ui/out-e2e, ui/dist, packaging/build, packaging/dist, packaging/ffmpeg-win64, packaging/deno-win64, native/*/publish and .serena/cache, matched with fnmatchcase; skip a file whose first 8000 bytes hold a NUL byte, reading each file once as bytes; and skip the scanner's own module by its resolved path."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:4040 — the issue names the vendored tree, the MCP bundle and discover.py:25,299"
      - "tools/issue_triage/discover.py:55 — EXCLUDED_PATHS already holds docs/execution, matched against the path from the scan root"
      - "C:/Temp/av-kit/triage-tool-fixes/discover-sim.txt — the round-0 rules over the real tree: 937 files walked, 0 candidates"
      - ".gitignore:12-43 — the generated, fetched and vendored trees: ui/out, ui/out-e2e, mcp-server/bundle, packaging/deno-win64, native/**/publish and the rest"
      - "C:/Temp/av-kit/triage-tool-fixes/discover-sim2.txt — the round-0 rules walk 110 files under 15 ignored trees; these rules walk 829 files, none under an ignored tree, with 0 candidates, and no tracked file lies under an added entry"
      - "C:/Temp/av-kit/ttf-plan-review-round-1.md — F1: ui/out, ui/out-e2e and packaging/deno-win64 markers are reported"
    research: { engine: none, sources: [] }
    reasoning: "Each rule removes one measured noise class and nothing else; the simulation leaves no candidate and the walk still reaches the repository's own code. The tree list mirrors every directory pattern in .gitignore, a slash-free pattern as a name and an anchored one as a repository path, so a tree that git treats as generated, fetched or vendored is never scanned, and the owned trees beside them (ui/src, mcp-server/src, the packaging spec and licence overrides, the native sources, the design notes) stay in scope. Reading .gitignore at run time lost because discover would need a gitignore parser for a file that rarely changes; the live smoke checks the fixed list against git's own ignored trees instead. Scanning only git ls-files lost because discover would then need git and a work tree to run. Excluding all of _inspiration lost because its design notes are av-kit's own text. Adding .jar to BINARY_EXTENSIONS alone lost because the next binary with another suffix would come back; the NUL test is the git heuristic and covers both. Skipping by resolved path, not by name, keeps a user file named discover.py in scope. Two-way: set entries and two checks."
  - id: D-949
    stage: planning
    question: "Where does triage --output put a dismissed issue?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "In archived, beside resolved issues. The actionable and deferred rules stay as they are, and triage-output.yaml is not regenerated in this session."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:4040 — the dismissed TTS-VOICE-SELECT-LAYOUT-JUMP lands in actionable"
      - "tools/issue_triage/verify.py:186 — verify_deep already treats resolved, candidate and dismissed as not active"
    research: { engine: none, sources: [] }
    reasoning: "A dismissed issue needs no work, so it does not belong in actionable, and the tool's own verify already groups it with resolved issues. Leaving TECH-DEBT, MONITORING and BLOCKED in actionable keeps today's triage rule: the issue lists them only as context. Regenerating triage-output.yaml lost because the next /issue-triage run regenerates it, and a mid-session rewrite of an ephemeral file adds a diff with no review value. Two-way: one condition."
  - id: D-950
    stage: planning
    question: "Which docs change with the tool?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The ten line edits of doc-check.py TABLE in issue-triage.md, the issue-triage SKILL.md, issue-lifecycle-guide.md, commands.md and cloud-local-collaboration.md, plus the --deep help text, and no other doc."
    source_tag: Local Canon
    precedents:
      - ".agent/workflows/issue-triage.md:93 — the workflow says verify --deep runs test-coverage scans and updates last_checked"
      - ".agent/docs/issue-lifecycle-guide.md:117-122 — five claims, three of which become false and one (fix indicators) never was true"
    research: { engine: none, sources: [] }
    reasoning: "Every line that would describe a check the tool no longer runs, or a write it no longer makes, changes; the rg sweep finds no other such line outside plans, handoffs and reflections, which record history. The lifecycle guide's line 549 sends a staleness question to verify --deep, which never checked staleness; it now names plain verify. .agent/docs/development-lifecycle.md:685 stays: its 'check test coverage' describes the agent's own manual check during triage, not what verify --deep runs, and an agent may still look for a test when it really re-checks an issue. Rewriting the docs' sections lost because the steps they describe still hold. Two-way: doc lines."
  - id: D-951
    stage: planning
    question: "Where and how are the tests written?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "One new tests/unit/test_issue_triage.py (LF) with tests named test_ac_N_ (N the AC number), markers built by concatenation, CLI cases run as a subprocess with an explicit child environment, and each test asserting its new name exists before using it."
    source_tag: Local Canon
    precedents:
      - "tests/unit/test_deps_report.py — a tools module tested under tests/unit through the pythonpath dot"
      - "P:/zorivest/tests/unit/test_issue_triage.py:2978-2996 — the cp1252 subprocess test of the same tool"
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:124 — tests/tooling belongs to Session 76"
    research: { engine: none, sources: [] }
    reasoning: "tests/unit avoids the Session 76 tree. A subprocess is the only way to give the CLI a cp1252 stream without reconfiguring pytest's own, and it also runs the real file path, which the package of the same name shadows on import. Built markers keep the test file out of discover's own results. Two-way: a test file."
  - id: D-953
    stage: planning
    question: "Against which path do discover's exclusions match, and what does a --root inside an excluded tree give?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Against the repository path: _repo_root returns the nearest of the resolved scan root and its parents that holds a .git entry, or the scan root when none does, and each directory is matched by its path from there. A scan root that lies in an excluded tree, by name or by path, gives no candidates."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/ttf-plan-review-round-1.md — F1: with --root mcp-server, bundle/index.mjs is reported"
      - "tools/issue_triage/discover.py:246-251 — today the multi-segment match is relative to the scan root"
      - "C:/Temp/av-kit/triage-tool-fixes/discover-sim2.txt — round-0 rules: --root mcp-server gives 3 bundle candidates; these rules: 0 from the root, mcp-server, ui and packaging, and nothing walked from mcp-server/bundle or ui/out"
    research: { engine: none, sources: [] }
    reasoning: "The exclusions name trees of this repository, so they mean something only from its root, which is how .gitignore anchors its own patterns. The .git entry finds that root without running git, and a .git file, as in a worktree, counts. Passing the repository root as a new scan_todos argument lost because every caller would have to know it, and the CLI has only --root and the working directory. Scanning a root inside an excluded tree anyway lost because the goal is that discover reports nothing from such a tree, and a scan from any higher root already skips it; returning nothing keeps the two the same. Two-way: one helper and one check."
  - id: D-952
    stage: planning
    question: "How is this session bounded against the others?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Its own session, not folded into Session 76; scope checks bound to row-0 content, not HEAD; the gate of §Session gate; the out-of-scope list of §Out of Scope."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md:182 — the split flag lets it merge into Session 76 only if that plan comes out small"
      - "docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md — the content-bound baseline of the same run"
    research: { engine: none, sources: [] }
    reasoning: "The coordinator's instruction for this run keeps Session 79 apart, and the two sessions share no file: Session 76 edits tests/tooling, this one tools/issue_triage and tests/unit. Binding to content lets Sessions 75 to 78 stay uncommitted without a false stop. Two-way: a plan boundary."
```

Expert pass (fresh context): 2 briefs. Holds: D-946. Changed: D-947. Not adopted: none. Receipt: `C:/Temp/av-kit/triage-tool-fixes/ttf-expert-pass.txt`; its facts rechecked in `ttf-expert-recheck.txt`.

### D-946: What happens to the "no test references this issue" finding that `verify --deep` gives for nearly every active issue?

**I recommend A: remove that check.** `verify --deep` then reports only a missing file. The check looks at every active issue (open or mitigated; it skips resolved and dismissed ones) and flags 42 of the 43 today; the one it skips, `CAPTURE-EXIF-SCANNED-ORIENTATION`, is the only active issue named in `tests/`. A missing test name is no signal: none of the 90 resolved issues is named in `tests/` either. The 42 lines bury the one useful finding. How A can fail: the tool no longer points out that an active or mitigated issue has no test naming it, so a triage that wants to know searches `tests/` itself. Undo cost: small; the check can come back as its own subcommand.

- B: narrow it to issues with `status: mitigated`. This is one condition and gives 1 finding today (`MCP-ELICITATION-VSCODE-AUTO-DECLINE`). It still loses: since 0 of the 90 resolved issues are named in a test, a mitigated issue without one is the normal case, not a warning. Narrowing it instead to issues whose record claims a test costs more, because no register field holds that claim.
- C: keep things as they are: every deep run prints one line per active issue, and each triage reads past them by hand, as the last two did.

Refs: `.agent/context/known-issues.yaml:4040` (`TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS`), `C:/Temp/av-kit/triage-tool-fixes/verify-deep.txt`, `C:/Temp/av-kit/ttf-expert-st.txt` (the census), `tools/issue_triage/verify.py:187`, D-812, M-6 (not M-11: the tool gates nothing), AC-5.

### D-947: Does `verify --deep` still write today's date into each issue's "last checked" field?

**I recommend A: no; `verify --deep` only reads the register.** The date is read as proof that someone checked the issue, and the canon sets it together with a method, a result and an evidence file (`cloud-local-collaboration.md:316`). The tool only checks whether a path exists, which is not a check of the issue, and for most issues it checks nothing, so its date is false evidence; the last triage had to undo it by restoring the file. After A, the triaging agent sets `verification.last_checked`, `method`, `result` and `evidence_file` together, by hand in the YAML, when it really re-checks an issue; the workflow note in `issue-triage.md` says so, and `doc-check.py` pins that text (AC-12). How A can fail: the 30 active issues whose date is the 2026-11-04 deep-run stamp show as stale in plain `verify` from 2026-12-05 (`verify.py:60` uses a strict `<`), then 5 more on 12-08, 2 on 12-09, 2 on 12-10 and 1 on 12-11. The flag is accurate, since nobody checked those issues on 11-04, and it costs little: no workflow step or gate runs plain `verify`, which already exits 1 today. Undo cost: small; the parameter can return.

- B: write the date only when a path check actually ran (the issue's own proposal). It loses because a path-exists test is not a check of the issue, and for most issues no path check runs: 29 of the 43 active issues already carry a date with no method or result, the shape B would keep producing.
- C: keep the parameter, but write the date only behind an opt-in `--stamp` flag. It is cheaper than B and loses for B's reason: the stamped date still records a check of the issue that did not happen.
- D: keep things as they are: every deep run rewrites the register with fresh dates for about 42 issues, and each triage restores the file by hand.

Refs: `.agent/context/known-issues.yaml:4040`, `ki-deep.yaml` against `ki-copy.yaml` in `C:/Temp/av-kit/triage-tool-fixes/`, `C:/Temp/av-kit/ttf-expert-lc.txt`, `tools/issue_triage/verify.py:60`, `tools/issue_triage/verify.py:238-242`, `.agent/docs/cloud-local-collaboration.md:316`, D-812, M-6, AC-6, AC-12.

## Research References

- Python `io.TextIOWrapper.reconfigure` (3.7+) changes the encoding of an open text stream; a stream that is not a `TextIOWrapper` has no `reconfigure` (`AttributeError`), and a stream with buffered output can refuse (`ValueError`), which the Zorivest guard and D-944 both suppress. Measured: `PYTHONIOENCODING=cp1252` reproduces the crash on any OS (`probe/help-cp1252.txt`).
- The NUL-byte test for binary files is git's own heuristic (`buffer_is_binary`, the first 8,000 bytes). Measured: both `.jar` candidates in the vendored tree hold a NUL byte in that window (`jar-nul-probe.txt`), and the simulation of all three rules leaves 0 candidates (`discover-sim.txt`).

## Planning receipts

All under `C:/Temp/av-kit/triage-tool-fixes/`, read-only against the repository; every probe of the register ran on a copy, and `pre-hash.txt` shows the real register's SHA-256 unchanged:

| Receipt | What it shows |
|---|---|
| `help-noenc.txt`, `probe/help-cp1252.txt` | `--help` exits 1 on `\u2192` with the console code page |
| `probe/bucket-fixture.yaml`, `probe/bucket-cp1252.txt`, `probe/bucket-utf8.txt` | `bucket` exits 1 on `\u26a0` under cp1252, and 0 under UTF-8 |
| `verify-deep.txt`, `ki-copy.yaml`, `ki-deep.yaml` | 51 findings (42 `no_test_coverage`, 9 prose `file_missing`) and 42 stamped dates on a copy |
| `resolution-path-census.txt` | 48 `resolution_path` values, 0 single path-shaped tokens |
| `discover-dry.txt`, `ki-disc.yaml` | 14 candidates: 9 vendored, 3 bundled, 2 self-matches |
| `discover-sim.txt` | The round-0 rules over the real tree: 937 files, 0 candidates |
| `ignored-dirs.txt`, `discover-sim2.py`, `discover-sim2.txt` | Git's ignored trees in the live tree (`.agent/` left out), and the round-0 against the round-1 rules from `.`, `mcp-server`, `ui`, `packaging`, `mcp-server/bundle` and `ui/out`: walked files under ignored trees 110 to 0, subroot bundle candidates 3 to 0, tracked files under the added entries 0 |
| `smoke-oracle-probe.txt` | `live-smoke.py`'s noise oracle classifies `ui/out`, `ui/out-e2e`, `packaging/deno-win64`, `mcp-server/bundle`, `native/*/publish`, `ui/test-results` and `.serena/cache` paths as noise and the `src` and packaging controls as not |
| `doc-check-anchor-probe.txt`, `doc-check-selftest.txt` | The doc table applies once per anchor with endings kept; the selftest passes 9 of 9 |
| `ruff-probe.txt`, `ruff-concise-probe.txt` | The four tool files' three existing ruff findings, and four files `ruff format` would change |
| `ttf-decision-probe.txt` | `decision_sources` on this plan and the grouping reads D-944 to D-953 and the grouping's D-813 to D-817; with `known-issues.yaml` and the two issues it adds D-812 |
| `jar-nul-probe.txt` | Both vendored `.jar` files hold a NUL byte in their first 8,000 bytes |
| `ttf-expert-pass.txt` | The §5a expert pass on D-946 and D-947: D-946 holds, D-947 changed (small); the reviewer's own receipts are `C:/Temp/av-kit/ttf-expert-*.txt` |
| `ttf-expert-recheck.txt` | The planner's recheck of the expert pass's facts: the census, the 2026-11-04 stamps, the strict `<` at `verify.py:60` and the first stale dates |
| `ttf-plan-task-lint.txt` | `lint_task_contract.py` on `task.md`: 29 rows, 27 fully checked, 2 `view_file` rows exempt |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the two issues, D-812 and the grouping §3 | `ttf-plan-2026-11-15-triage-tool-fixes` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-1 to AC-14 | `ttf-execution-2026-11-15-triage-tool-fixes` |
